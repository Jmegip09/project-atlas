"""
Loads clean purchase order data from the raw CSVs into PostgreSQL.

This is the last stage of the pipeline: generate_data.py produces raw,
source-system-style extracts -> run_validation.py flags the bad rows ->
load.py loads everything EXCEPT what got flagged.

Business keys (supplier_name, sku) in the raw CSVs are resolved against
master data already in the database (suppliers, products) to get the
real surrogate IDs (supplier_id, product_id) the purchase_orders and
purchase_order_lines tables actually require.

Assumes master data (suppliers, products, warehouses) has already been
loaded via sql/seed/01-03. Run run_validation.py first so the data
quality log exists.

Run from the project root:
    python -m python.etl.load
"""
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from config.settings import RAW_DATA_DIR, DATA_QUALITY_LOG_PATH
from utils.db import get_engine


def load_clean_rows():
    engine = get_engine()

    headers_path = Path(RAW_DATA_DIR) / "purchase_orders_raw.csv"
    lines_path = Path(RAW_DATA_DIR) / "purchase_order_lines_raw.csv"
    quality_log_path = Path(DATA_QUALITY_LOG_PATH)

    if not headers_path.exists() or not lines_path.exists():
        sys.exit("Raw CSVs not found. Run 'python -m python.etl.generate_data' first.")
    if not quality_log_path.exists():
        sys.exit("Data quality log not found. Run 'python -m python.validation.run_validation' first.")

    headers_df = pd.read_csv(headers_path, dtype=str)
    lines_df = pd.read_csv(lines_path)
    issues_df = pd.read_csv(quality_log_path)

    # --- Split flagged record_ids back into header vs. line issues ---
    # Header issues are flagged by bare po_number (e.g. "PO-2026-1010").
    # Line issues are flagged as "po_number:sku" (e.g. "PO-2026-1000:PROD-SKU-1001").
    bad_po_numbers = set(issues_df.loc[~issues_df["record_id"].str.contains(":"), "record_id"])
    bad_line_ids = set(issues_df.loc[issues_df["record_id"].str.contains(":"), "record_id"])

    # --- Clean headers: drop anything flagged at the header level ---
    clean_headers = headers_df[~headers_df["po_number"].isin(bad_po_numbers)].copy()

    # --- Clean lines: drop lines flagged directly, AND lines belonging to a bad header ---
    lines_df["line_record_id"] = lines_df["po_number"] + ":" + lines_df["sku"]
    clean_lines = lines_df[
        ~lines_df["line_record_id"].isin(bad_line_ids)
        & ~lines_df["po_number"].isin(bad_po_numbers)
    ].copy()
    clean_lines = clean_lines.drop(columns=["line_record_id"])

    skipped_headers = len(headers_df) - len(clean_headers)
    skipped_lines = len(lines_df) - len(clean_lines)

    with engine.begin() as conn:
        # --- Resolve business keys to surrogate IDs from master data ---
        suppliers = pd.read_sql("SELECT supplier_id, supplier_name FROM suppliers", conn)
        products = pd.read_sql("SELECT product_id, sku FROM products", conn)

        # --- Idempotency: skip PO numbers already loaded from a prior run ---
        already_loaded = pd.read_sql("SELECT po_number FROM purchase_orders", conn)
        already_loaded_set = set(already_loaded["po_number"])
        already_loaded_count = clean_headers["po_number"].isin(already_loaded_set).sum()
        clean_headers = clean_headers[~clean_headers["po_number"].isin(already_loaded_set)]
        if already_loaded_count:
            print(f"Skipping {already_loaded_count} PO(s) already loaded from a previous run.")

        pending_headers = len(clean_headers)
        clean_headers = clean_headers.merge(suppliers, on="supplier_name", how="inner")
        # merge can silently drop rows whose supplier isn't in master data even
        # though validators.py should have already caught that -- surface it loudly
        unresolved = pending_headers - len(clean_headers)
        if unresolved:
            print(f"WARNING: {unresolved} 'clean' header(s) had a supplier_name "
                  f"that didn't resolve to master data. Skipped.")

        # --- Insert headers one at a time so we can capture po_id per po_number ---
        po_number_to_id = {}
        for _, row in clean_headers.iterrows():
            result = conn.execute(
                text("""
                    INSERT INTO purchase_orders
                        (po_number, supplier_id, order_date, expected_delivery_date, po_status)
                    VALUES
                        (:po_number, :supplier_id, :order_date, :expected_delivery_date, :po_status)
                    RETURNING po_id
                """),
                {
                    "po_number": row["po_number"],
                    "supplier_id": int(row["supplier_id"]),
                    "order_date": row["order_date"],
                    "expected_delivery_date": row["expected_delivery_date"],
                    "po_status": row["po_status"],
                },
            )
            po_number_to_id[row["po_number"]] = result.scalar_one()

        # --- Resolve lines to their real po_id and product_id, then bulk insert ---
        clean_lines["po_id"] = clean_lines["po_number"].map(po_number_to_id)
        clean_lines = clean_lines.merge(products, on="sku", how="inner")

        unresolved_lines = len(
            lines_df[
                ~lines_df["po_number"].isin(bad_po_numbers)
                & lines_df["po_number"].isin(po_number_to_id)
            ]
        ) - len(clean_lines)

        lines_to_insert = clean_lines[
            ["po_id", "product_id", "quantity_ordered", "quantity_received", "unit_cost"]
        ].dropna(subset=["po_id"])

        if not lines_to_insert.empty:
            lines_to_insert.to_sql(
                "purchase_order_lines", conn, if_exists="append", index=False
            )

    print(f"Loaded {len(po_number_to_id)} clean PO headers "
          f"({skipped_headers} skipped for data quality issues).")
    print(f"Loaded {len(lines_to_insert)} clean PO lines "
          f"({skipped_lines} skipped for data quality issues).")


if __name__ == "__main__":
    load_clean_rows()
    