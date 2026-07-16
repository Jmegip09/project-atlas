"""
Loads clean purchase order data from the raw CSVs into PostgreSQL.

This is the last stage of the pipeline: generate_data.py produces raw,
source-system-style extracts -> run_validation.py flags the bad rows ->
load.py loads everything EXCEPT what got flagged. What counts as "clean"
lives in clean_rows.py, shared with generate_receiving_raw.py so the two
scripts can't quietly disagree on it.

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
import pandas as pd
from sqlalchemy import text

from etl.clean_rows import load_raw_po_data, get_clean_po_lines
from utils.db import get_engine


def load_clean_rows():
    engine = get_engine()

    headers_df, lines_df, issues_df = load_raw_po_data()
    clean_headers, clean_lines = get_clean_po_lines(headers_df, lines_df, issues_df)

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