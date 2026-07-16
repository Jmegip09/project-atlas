"""
Shared logic for filtering raw purchase order CSVs down to clean rows,
using the data quality log run_validation.py already produced.

This exists so load.py (loads clean POs to Postgres) and
generate_receiving_raw.py (derives receiving events from clean POs) can't
silently drift on what "clean" means -- there's exactly one definition,
used by both.
"""
from pathlib import Path

import pandas as pd

from config.settings import RAW_DATA_DIR, DATA_QUALITY_LOG_PATH


def load_raw_po_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Reads the raw PO CSVs + quality log. Raises if any stage hasn't run yet."""
    headers_path = Path(RAW_DATA_DIR) / "purchase_orders_raw.csv"
    lines_path = Path(RAW_DATA_DIR) / "purchase_order_lines_raw.csv"
    quality_log_path = Path(DATA_QUALITY_LOG_PATH)

    if not headers_path.exists() or not lines_path.exists():
        raise SystemExit("Raw CSVs not found. Run 'python -m python.etl.generate_data' first.")
    if not quality_log_path.exists():
        raise SystemExit("Data quality log not found. Run 'python -m python.validation.run_validation' first.")

    headers_df = pd.read_csv(headers_path, dtype=str)
    lines_df = pd.read_csv(lines_path)
    issues_df = pd.read_csv(quality_log_path)
    return headers_df, lines_df, issues_df


def get_clean_po_lines(
    headers_df: pd.DataFrame, lines_df: pd.DataFrame, issues_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (clean_headers, clean_lines): every row NOT flagged by the
    validators, with lines belonging to a bad header excluded too (a line
    isn't "clean" if its own parent PO is broken, even if the line itself
    passed every check).
    """
    # Header issues are flagged by bare po_number (e.g. "PO-2026-1010").
    # Line issues are flagged as "po_number:sku" (e.g. "PO-2026-1000:PROD-SKU-1001").
    bad_po_numbers = set(issues_df.loc[~issues_df["record_id"].str.contains(":"), "record_id"])
    bad_line_ids = set(issues_df.loc[issues_df["record_id"].str.contains(":"), "record_id"])

    clean_headers = headers_df[~headers_df["po_number"].isin(bad_po_numbers)].copy()

    lines_df = lines_df.copy()
    lines_df["line_record_id"] = lines_df["po_number"] + ":" + lines_df["sku"]
    clean_lines = lines_df[
        ~lines_df["line_record_id"].isin(bad_line_ids)
        & ~lines_df["po_number"].isin(bad_po_numbers)
    ].drop(columns=["line_record_id"])

    return clean_headers, clean_lines