"""
Validation rules for Project Atlas ETL.

Each function takes a pandas DataFrame (raw purchase_orders or
purchase_order_lines) and returns a list of flagged issues, not a
boolean and not a filtered dataframe. Every issue records which
record failed, which rule it broke, and why -- that's what makes
data_quality_log.csv a real audit trail instead of a pass/fail flag.
"""
import pandas as pd

VALID_SUPPLIERS = {
    "Apex Logistics Group",
    "Global Core Manufacturing",
    "Titan Industrial Supply",
    "Beacon Packaging Corp",
}

VALID_SKUS = {
    "PROD-SKU-1001",
    "PROD-SKU-1002",
    "PROD-SKU-2001",
    "PROD-SKU-3001",
    "PROD-SKU-4001",
}

VALID_PO_STATUSES = {"Open", "Partially Received", "Fully Received", "Cancelled"}


def _issue(record_id, rule_id, field, value, description):
    return {
        "record_id": record_id,
        "rule_id": rule_id,
        "field": field,
        "value": value,
        "description": description,
    }


# ---------------------------------------------------------------------------
# Header-level validators (purchase_orders_raw.csv)
# ---------------------------------------------------------------------------

def check_duplicate_po_numbers(df: pd.DataFrame) -> list[dict]:
    dupes = df[df.duplicated(subset="po_number", keep=False)]
    return [
        _issue(row["po_number"], "SCHEMA-uq_po_number", "po_number", row["po_number"],
               "Duplicate PO number found in raw extract.")
        for _, row in dupes.iterrows()
    ]


def check_missing_supplier(df: pd.DataFrame) -> list[dict]:
    missing = df[df["supplier_name"].isna() | (df["supplier_name"].str.strip() == "")]
    return [
        _issue(row["po_number"], "ATLAS-RULE-001", "supplier_name", row["supplier_name"],
               "Purchase order has no supplier reference.")
        for _, row in missing.iterrows()
    ]


def check_unknown_supplier(df: pd.DataFrame) -> list[dict]:
    known = df[df["supplier_name"].notna() & (df["supplier_name"].str.strip() != "")]
    unknown = known[~known["supplier_name"].isin(VALID_SUPPLIERS)]
    return [
        _issue(row["po_number"], "ATLAS-RULE-001", "supplier_name", row["supplier_name"],
               "Supplier name does not match any known supplier in master data.")
        for _, row in unknown.iterrows()
    ]


def check_delivery_before_order(df: pd.DataFrame) -> list[dict]:
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["expected_delivery_date"] = pd.to_datetime(df["expected_delivery_date"], errors="coerce")
    bad = df[df["expected_delivery_date"] < df["order_date"]]
    return [
        _issue(row["po_number"], "SCHEMA-chk_delivery_date", "expected_delivery_date",
               row["expected_delivery_date"], "Expected delivery date is before the order date.")
        for _, row in bad.iterrows()
    ]


def check_blank_status(df: pd.DataFrame) -> list[dict]:
    blank = df[df["po_status"].isna() | (df["po_status"].str.strip() == "")]
    return [
        _issue(row["po_number"], "SCHEMA-not-null-po_status", "po_status", row["po_status"],
               "Purchase order is missing a status.")
        for _, row in blank.iterrows()
    ]


def check_invalid_status(df: pd.DataFrame) -> list[dict]:
    present = df[df["po_status"].notna() & (df["po_status"].str.strip() != "")]
    bad = present[~present["po_status"].isin(VALID_PO_STATUSES)]
    return [
        _issue(row["po_number"], "SCHEMA-chk_po_status", "po_status", row["po_status"],
               "PO status is not one of the allowed values.")
        for _, row in bad.iterrows()
    ]


HEADER_VALIDATORS = [
    check_duplicate_po_numbers,
    check_missing_supplier,
    check_unknown_supplier,
    check_delivery_before_order,
    check_blank_status,
    check_invalid_status,
]


# ---------------------------------------------------------------------------
# Line-level validators (purchase_order_lines_raw.csv)
# ---------------------------------------------------------------------------

def check_negative_quantity(df: pd.DataFrame) -> list[dict]:
    bad = df[df["quantity_ordered"] < 0]
    return [
        _issue(f"{row['po_number']}:{row['sku']}", "SCHEMA-chk_quantity_positive",
               "quantity_ordered", row["quantity_ordered"], "Quantity ordered is negative.")
        for _, row in bad.iterrows()
    ]


def check_over_received(df: pd.DataFrame) -> list[dict]:
    bad = df[df["quantity_received"] > df["quantity_ordered"]]
    return [
        _issue(f"{row['po_number']}:{row['sku']}", "SCHEMA-chk_received_vs_ordered",
               "quantity_received", row["quantity_received"],
               "Quantity received exceeds quantity ordered.")
        for _, row in bad.iterrows()
    ]


def check_unknown_sku(df: pd.DataFrame) -> list[dict]:
    bad = df[~df["sku"].isin(VALID_SKUS)]
    return [
        _issue(f"{row['po_number']}:{row['sku']}", "FK-product_sku", "sku", row["sku"],
               "SKU does not match any known product in master data.")
        for _, row in bad.iterrows()
    ]


def check_zero_or_negative_cost(df: pd.DataFrame) -> list[dict]:
    bad = df[df["unit_cost"] <= 0]
    return [
        _issue(f"{row['po_number']}:{row['sku']}", "SCHEMA-chk_unit_cost", "unit_cost",
               row["unit_cost"], "Unit cost is zero or negative.")
        for _, row in bad.iterrows()
    ]


LINE_VALIDATORS = [
    check_negative_quantity,
    check_over_received,
    check_unknown_sku,
    check_zero_or_negative_cost,
]


def run_all(headers_df: pd.DataFrame, lines_df: pd.DataFrame) -> pd.DataFrame:
    """Runs every validator, returns one combined DataFrame of every issue found."""
    issues = []
    for validator in HEADER_VALIDATORS:
        issues.extend(validator(headers_df))
    for validator in LINE_VALIDATORS:
        issues.extend(validator(lines_df))

    return pd.DataFrame(issues, columns=["record_id", "rule_id", "field", "value", "description"])


# ---------------------------------------------------------------------------
# Receiving event validators (receiving_events_raw.csv)
# ---------------------------------------------------------------------------

KNOWN_WAREHOUSE_CODES = {"WH-ORL-01", "WH-MIA-02", "WH-TPA-03"}


def _receiving_record_id(row) -> str:
    return f"{row['po_number']}:{row['sku']}:{row['event_number']}"


def check_receiving_quantity_mismatch(df: pd.DataFrame) -> list[dict]:
    bad = df[
        df["quantity_accepted"] + df["quantity_damaged"] + df["quantity_rejected"]
        != df["quantity_received"]
    ]
    return [
        _issue(_receiving_record_id(row), "SCHEMA-chk_receiving_quality_breakdown",
               "quantity_received", row["quantity_received"],
               "Accepted + damaged + rejected does not equal quantity received.")
        for _, row in bad.iterrows()
    ]


def check_receiving_negative_quantities(df: pd.DataFrame) -> list[dict]:
    bad = df[
        (df["quantity_accepted"] < 0) | (df["quantity_damaged"] < 0)
        | (df["quantity_rejected"] < 0) | (df["quantity_received"] <= 0)
    ]
    return [
        _issue(_receiving_record_id(row), "SCHEMA-chk_receiving_quality_nonnegative",
               "quantity_damaged", row["quantity_damaged"],
               "Receiving event has a negative or non-positive quantity.")
        for _, row in bad.iterrows()
    ]


def check_receiving_before_order(df: pd.DataFrame) -> list[dict]:
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["received_date"] = pd.to_datetime(df["received_date"], errors="coerce")
    bad = df[df["received_date"] < df["order_date"]]
    return [
        _issue(_receiving_record_id(row), "LOGIC-received_before_ordered", "received_date",
               row["received_date"], "Item was received before the PO was even ordered.")
        for _, row in bad.iterrows()
    ]


def check_receiving_unknown_warehouse(df: pd.DataFrame) -> list[dict]:
    bad = df[~df["warehouse_code"].isin(KNOWN_WAREHOUSE_CODES)]
    return [
        _issue(_receiving_record_id(row), "FK-warehouse_code", "warehouse_code",
               row["warehouse_code"], "Warehouse code does not match any known warehouse.")
        for _, row in bad.iterrows()
    ]


def check_receiving_duplicate_event(df: pd.DataFrame) -> list[dict]:
    key = df["po_number"] + ":" + df["sku"] + ":" + df["event_number"].astype(str)
    dupes = df[key.duplicated(keep=False)]
    return [
        _issue(_receiving_record_id(row), "SCHEMA-uq_receiving_po_line_event",
               "event_number", row["event_number"],
               "Duplicate receiving event for this PO line.")
        for _, row in dupes.iterrows()
    ]


RECEIVING_VALIDATORS = [
    check_receiving_quantity_mismatch,
    check_receiving_negative_quantities,
    check_receiving_before_order,
    check_receiving_unknown_warehouse,
    check_receiving_duplicate_event,
]


def run_receiving_validation(events_df: pd.DataFrame) -> pd.DataFrame:
    issues = []
    for validator in RECEIVING_VALIDATORS:
        issues.extend(validator(events_df))
    return pd.DataFrame(issues, columns=["record_id", "rule_id", "field", "value", "description"])