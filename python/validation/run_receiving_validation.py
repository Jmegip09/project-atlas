"""
Loads the raw receiving events CSV, runs the receiving validator suite,
writes a receiving-specific data quality log, and prints a summary.

Run AFTER generate_receiving_raw.py:
    python -m python.validation.run_receiving_validation
"""
import pandas as pd
from pathlib import Path

from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR
from validation.validators import run_receiving_validation

RECEIVING_QUALITY_LOG_PATH = f"{PROCESSED_DATA_DIR}/receiving_quality_log.csv"


def main():
    events_path = Path(RAW_DATA_DIR) / "receiving_events_raw.csv"
    events_df = pd.read_csv(events_path)

    numeric_cols = ["quantity_received", "quantity_accepted", "quantity_damaged", "quantity_rejected"]
    for col in numeric_cols:
        events_df[col] = pd.to_numeric(events_df[col], errors="coerce")

    issues_df = run_receiving_validation(events_df)

    output_path = Path(RECEIVING_QUALITY_LOG_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    issues_df.to_csv(output_path, index=False)

    print(f"Checked {len(events_df)} receiving events.")
    print(f"Found {len(issues_df)} issues -> {output_path}")
    if not issues_df.empty:
        print(issues_df["rule_id"].value_counts())


if __name__ == "__main__":
    main()