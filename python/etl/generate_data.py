"""
Generates a raw, source-system-style batch of purchase order data.

Mimics what a real supplier/ERP extract looks like: natural/business
keys only (no internal DB IDs), and a deliberate percentage of
defective records for validators.py to catch downstream.

Run from the project root:
    python -m python.etl.generate_data
"""

import csv
import random
import uuid
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

from config.settings import RAW_DATA_DIR

fake = Faker()
Faker.seed(42)     # reproducible output while you're building validators
random.seed(42)

# ---------------------------------------------------------------------------
# Business keys, matching what's actually in sql/seed/*.sql right now.
# transform.py will resolve these to real supplier_id / product_id /
# warehouse_id later in the pipeline — this script doesn't touch the DB.
# ---------------------------------------------------------------------------
SUPPLIER_NAMES = [
    "Apex Logistics Group",
    "Global Core Manufacturing",
    "Titan Industrial Supply",
    "Beacon Packaging Corp",
]

PRODUCT_SKUS = [
    "PROD-SKU-1001",
    "PROD-SKU-1002",
    "PROD-SKU-2001",
    "PROD-SKU-3001",
    "PROD-SKU-4001",
]

WAREHOUSE_CODES = ["WH-ORL-01", "WH-MIA-02", "WH-TPA-03"]

PO_STATUSES = ["Open", "Partially Received", "Fully Received", "Cancelled"]

HEADER_COUNT = 40          # how many PO headers to generate
DEFECT_RATE = 0.15         # ~15% of headers get a deliberate problem
LINES_PER_PO = (1, 4)      # random min/max lines per PO


def generate_po_headers(count: int) -> list[dict]:
    """
    Builds PO header rows. Each row has a chance of being defective —
    the defect type is recorded in a hidden-from-CSV way (we just build
    it in) so validators.py has real, known problems to find.
    """
    headers = []
    used_po_numbers = set()

    for i in range(count):
        order_date = fake.date_between(start_date="-90d", end_date="today")
        expected_delivery = order_date + timedelta(days=random.randint(3, 21))
        po_number = f"PO-{2026}-{1000 + i}"

        row = {
            "po_number": po_number,
            "supplier_name": random.choice(SUPPLIER_NAMES),
            "order_date": order_date.isoformat(),
            "expected_delivery_date": expected_delivery.isoformat(),
            "po_status": random.choice(PO_STATUSES),
        }

        # --- Deliberate defect injection ---
        if random.random() < DEFECT_RATE:
            defect = random.choice([
                "duplicate_po_number",
                "missing_supplier",
                "bad_date_logic",
                "unknown_supplier",
                "blank_status",
            ])

            if defect == "duplicate_po_number" and headers:
                row["po_number"] = headers[-1]["po_number"]
            elif defect == "missing_supplier":
                row["supplier_name"] = ""
            elif defect == "bad_date_logic":
                # expected delivery BEFORE the order was even placed
                row["expected_delivery_date"] = (order_date - timedelta(days=5)).isoformat()
            elif defect == "unknown_supplier":
                row["supplier_name"] = "Nonexistent Vendor LLC"
            elif defect == "blank_status":
                row["po_status"] = ""

        used_po_numbers.add(row["po_number"])
        headers.append(row)

    return headers


def generate_po_lines(headers: list[dict]) -> list[dict]:
    """
    Builds line-item rows tied to each header's po_number.
    A line's quantity_received should never exceed quantity_ordered —
    that's a real constraint in the schema, so we mostly respect it,
    but sometimes deliberately violate it.
    """
    lines = []

    for header in headers:
        num_lines = random.randint(*LINES_PER_PO)
        chosen_skus = random.sample(PRODUCT_SKUS, k=min(num_lines, len(PRODUCT_SKUS)))

        for sku in chosen_skus:
            quantity_ordered = random.randint(10, 500)
            quantity_received = 0
            if header["po_status"] in ("Partially Received", "Fully Received"):
                quantity_received = random.randint(0, quantity_ordered)

            row = {
                "po_number": header["po_number"],
                "sku": sku,
                "quantity_ordered": quantity_ordered,
                "quantity_received": quantity_received,
                "unit_cost": round(random.uniform(5, 500), 2),
            }

            if random.random() < DEFECT_RATE:
                defect = random.choice([
                    "negative_quantity",
                    "over_received",
                    "unknown_sku",
                    "zero_cost",
                ])
                if defect == "negative_quantity":
                    row["quantity_ordered"] = -abs(quantity_ordered)
                elif defect == "over_received":
                    row["quantity_received"] = quantity_ordered + random.randint(10, 50)
                elif defect == "unknown_sku":
                    row["sku"] = "PROD-SKU-9999"
                elif defect == "zero_cost":
                    row["unit_cost"] = 0

            lines.append(row)

    return lines


def write_csv(rows: list[dict], filename: str) -> None:
    output_dir = Path(RAW_DATA_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows -> {filepath}")


def main():
    headers = generate_po_headers(HEADER_COUNT)
    lines = generate_po_lines(headers)

    write_csv(headers, "purchase_orders_raw.csv")
    write_csv(lines, "purchase_order_lines_raw.csv")


if __name__ == "__main__":
    main()