"""
Generates a raw, source-system-style receiving event extract, DERIVED from
purchase order lines -- never invented independently. This mirrors how a
real WMS/EDI receiving feed would look: natural/business keys only (no
internal DB IDs -- same convention as generate_data.py), denormalized
(order_date/warehouse_code carried along as a real extract would), and a
deliberate percentage of messy/defective rows for the validator to catch
downstream.

Reads directly from the raw PO CSVs + data quality log -- no database
required for this stage. po_number/sku are resolved to real po_line_id
only later, at load_receiving.py time, same as how load.py resolves
supplier_name/sku to surrogate IDs only at its own load time.

Flow per clean PO line with quantity_received > 0:
    PO line's recorded quantity_received becomes the TOTAL accepted units
    across 1-2 receiving events (supplier_profiles decide split odds).
    Each event's gross quantity_received = accepted + damaged + rejected,
    so a shipment can show MORE units physically arriving at the dock than
    ultimately went into sellable inventory.

Run AFTER run_validation.py (needs the PO quality log to know what's clean):
    python -m python.etl.generate_receiving_raw
"""
import csv
import random
from datetime import timedelta
from pathlib import Path

import pandas as pd

from config.profiles import (
    SUPPLIER_PROFILES, DEFAULT_SUPPLIER_PROFILE,
    WAREHOUSE_PROFILES, DEFAULT_WAREHOUSE_PROFILE,
)
from config.settings import RAW_DATA_DIR
from etl.clean_rows import load_raw_po_data, get_clean_po_lines

random.seed(42)

DEFECT_RATE = 0.15
WAREHOUSE_CODES = list(WAREHOUSE_PROFILES.keys())


def fetch_source_lines():
    """Clean PO lines with an actual receipt, plus everything needed to simulate one.
    Sourced entirely from the raw CSVs + quality log -- no DB round-trip."""
    headers_df, lines_df, issues_df = load_raw_po_data()
    clean_headers, clean_lines = get_clean_po_lines(headers_df, lines_df, issues_df)

    merged = clean_lines.merge(
        clean_headers[["po_number", "order_date", "expected_delivery_date", "supplier_name"]],
        on="po_number", how="inner",
    )
    merged["order_date"] = pd.to_datetime(merged["order_date"])
    merged["expected_delivery_date"] = pd.to_datetime(merged["expected_delivery_date"])
    merged = merged.rename(columns={"quantity_received": "total_accepted"})
    merged = merged[merged["total_accepted"] > 0]

    return merged[["po_number", "sku", "total_accepted", "order_date",
                    "expected_delivery_date", "supplier_name"]]


def pick_warehouse(rng_choice_pool):
    return rng_choice_pool[random.randrange(len(rng_choice_pool))]


def split_accepted(total_accepted: int, num_events: int) -> list[int]:
    """Splits total_accepted across events, e.g. 95 -> [80, 15]."""
    if num_events == 1:
        return [total_accepted]
    first = max(1, round(total_accepted * random.uniform(0.55, 0.85)))
    first = min(first, total_accepted - 1) if total_accepted > 1 else total_accepted
    return [first, total_accepted - first]


def simulate_event(accepted: int, event_index: int, order_date, expected_delivery,
                    supplier_profile: dict, warehouse_code: str) -> dict:
    order_date = pd.Timestamp(order_date)
    expected_delivery = pd.Timestamp(expected_delivery)
    wh_profile = WAREHOUSE_PROFILES.get(warehouse_code, DEFAULT_WAREHOUSE_PROFILE)

    damaged = round(accepted * supplier_profile["damage_probability"] * random.uniform(0.5, 1.5))
    rejected = round(accepted * supplier_profile["rejection_probability"] * random.uniform(0.5, 1.5))
    gross_received = accepted + damaged + rejected

    on_time = random.random() < supplier_profile["on_time_probability"]
    window = max((expected_delivery - order_date).days, 1)
    if on_time:
        offset_days = random.randint(max(window - 3, 0), window)
    else:
        offset_days = random.randint(window + 1, window + 10)
    # later events in a multi-shipment line land after the first
    offset_days += event_index * random.randint(2, 6)

    delay_hours = random.uniform(*wh_profile["inspection_delay_hours"])
    received_date = order_date + timedelta(days=offset_days, hours=delay_hours)

    return {
        "quantity_received": gross_received,
        "quantity_accepted": accepted,
        "quantity_damaged": damaged,
        "quantity_rejected": rejected,
        "received_date": received_date.isoformat(sep=" "),
        "warehouse_code": warehouse_code,
    }


def generate_events(source_df: pd.DataFrame) -> list[dict]:
    events = []

    for _, line in source_df.iterrows():
        profile = SUPPLIER_PROFILES.get(line["supplier_name"], DEFAULT_SUPPLIER_PROFILE)
        num_events = 2 if random.random() < profile["partial_receipt_probability"] else 1
        splits = split_accepted(int(line["total_accepted"]), num_events)
        warehouse_code = pick_warehouse(WAREHOUSE_CODES)

        for event_index, accepted in enumerate(splits, start=1):
            event = simulate_event(
                accepted, event_index - 1, line["order_date"], line["expected_delivery_date"],
                profile, warehouse_code,
            )
            row = {
                "po_number": line["po_number"],
                "sku": line["sku"],
                "event_number": event_index,
                "order_date": line["order_date"].isoformat(),
                **event,
            }

            # --- Deliberate defect injection, same spirit as generate_data.py ---
            if random.random() < DEFECT_RATE:
                defect = random.choice([
                    "quantity_mismatch", "received_before_ordered",
                    "duplicate_event", "unknown_warehouse", "negative_damaged",
                ])
                if defect == "quantity_mismatch":
                    row["quantity_received"] += random.randint(3, 10)  # breaks accepted+damaged+rejected sum
                elif defect == "received_before_ordered":
                    row["received_date"] = (line["order_date"] - timedelta(days=4)).isoformat()
                elif defect == "duplicate_event":
                    events.append(dict(row))  # append twice on purpose
                elif defect == "unknown_warehouse":
                    row["warehouse_code"] = "WH-XXX-99"
                elif defect == "negative_damaged":
                    row["quantity_damaged"] = -abs(row["quantity_damaged"] or 1)

            events.append(row)

    return events


def write_csv(rows: list[dict], filename: str) -> None:
    output_dir = Path(RAW_DATA_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename

    fieldnames = ["po_number", "sku", "event_number", "order_date", "received_date",
                  "warehouse_code", "quantity_received", "quantity_accepted",
                  "quantity_damaged", "quantity_rejected"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows -> {filepath}")


def main():
    source_df = fetch_source_lines()
    if source_df.empty:
        raise SystemExit("No received PO lines found. Run load.py first.")

    events = generate_events(source_df)
    write_csv(events, "receiving_events_raw.csv")


if __name__ == "__main__":
    main()