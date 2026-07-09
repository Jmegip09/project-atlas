"""
Loads the raw CSVs, runs the full validator suite, writes the data
quality log, and prints a summary.

Run from the project root:
    python -m python.validation.run_validation
"""
import pandas as pd
from pathlib import Path

from config.settings import RAW_DATA_DIR, DATA_QUALITY_LOG_PATH
from validation.validators import run_all


def main():
    headers_path = Path(RAW_DATA_DIR) / "purchase_orders_raw.csv"
    lines_path = Path(RAW_DATA_DIR) / "purchase_order_lines_raw.csv"

    # dtype=str on headers: we want to check blank/missing values ourselves,
    # not have pandas silently turn "" into NaN before our checks even run
    headers_df = pd.read_csv(headers_path, dtype=str)
    lines_df = pd.read_csv(lines_path)

    lines_df["quantity_ordered"] = pd.to_numeric(lines_df["quantity_ordered"], errors="coerce")
    lines_df["quantity_received"] = pd.to_numeric(lines_df["quantity_received"], errors="coerce")
    lines_df["unit_cost"] = pd.to_numeric(lines_df["unit_cost"], errors="coerce")

    issues_df = run_all(headers_df, lines_df)

    output_path = Path(DATA_QUALITY_LOG_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    issues_df.to_csv(output_path, index=False)

    print(f"Checked {len(headers_df)} PO headers and {len(lines_df)} PO lines.")
    print(f"Found {len(issues_df)} issues -> {output_path}")
    if not issues_df.empty:
        print(issues_df["rule_id"].value_counts())


if __name__ == "__main__":
    main()