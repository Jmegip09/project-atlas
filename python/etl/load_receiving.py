"""
Derives receiving_transactions records from purchase_order_lines that show
an actual receipt (quantity_received > 0).

Project Atlas doesn't have a real WMS scanning receipts in real time, so
this script is a stand-in for that feed: for every PO line that shows units
received, it creates one receiving_transactions row -- picking a plausible
warehouse from inventory_balances (which warehouses actually stock that
product) and a plausible received_date between the PO's order_date and
expected_delivery_date (sometimes a few days late, deliberately, so
receiving-bottleneck queries have something real to find).

This is synthetic-but-consistent data, same spirit as generate_data.py.
It is NOT a substitute for a real receiving feed -- documented as a known
simplification in README/ROADMAP.

Run from the project root, AFTER load.py:
    python -m python.etl.load_receiving
"""
import random
from datetime import timedelta

import pandas as pd
from sqlalchemy import text

from utils.db import get_engine

random.seed(42)


def load_receiving():
    engine = get_engine()

    with engine.begin() as conn:
        lines = pd.read_sql(
            """
            SELECT pol.po_line_id, pol.product_id, pol.quantity_received,
                   po.order_date, po.expected_delivery_date
            FROM purchase_order_lines pol
            JOIN purchase_orders po ON po.po_id = pol.po_id
            WHERE pol.quantity_received > 0
            """,
            conn,
        )

        already_received = pd.read_sql(
            "SELECT DISTINCT po_line_id FROM receiving_transactions", conn
        )
        already_received_set = set(already_received["po_line_id"])
        pending = lines[~lines["po_line_id"].isin(already_received_set)]
        skipped = len(lines) - len(pending)

        # product_id -> list of warehouse_ids that actually stock it
        stocking = pd.read_sql(
            "SELECT DISTINCT product_id, warehouse_id FROM inventory_balances", conn
        )
        stocking_map = stocking.groupby("product_id")["warehouse_id"].apply(list).to_dict()
        all_warehouse_ids = pd.read_sql("SELECT warehouse_id FROM warehouses", conn)[
            "warehouse_id"
        ].tolist()

        rows = []
        for _, row in pending.iterrows():
            candidates = stocking_map.get(row["product_id"], all_warehouse_ids)
            warehouse_id = random.choice(candidates)

            # Received sometime between order_date and expected_delivery_date + 0-5 days
            # (the +5 gives us realistic "late" receipts to detect in reporting)
            window_days = (row["expected_delivery_date"] - row["order_date"]).days
            offset = random.randint(max(window_days - 2, 1), window_days + 5)
            received_date = row["order_date"] + timedelta(days=offset)

            rows.append({
                "po_line_id": int(row["po_line_id"]),
                "warehouse_id": int(warehouse_id),
                "quantity_received": int(row["quantity_received"]),
                "received_date": received_date,
            })

        if rows:
            pd.DataFrame(rows).to_sql(
                "receiving_transactions", conn, if_exists="append", index=False
            )

    print(f"Loaded {len(rows)} receiving transactions "
          f"({skipped} skipped, already loaded from a previous run).")


if __name__ == "__main__":
    load_receiving()
    