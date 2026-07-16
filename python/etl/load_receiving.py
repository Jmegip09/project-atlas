"""
Loads clean receiving events into receiving_transactions, and drives the
inventory_transactions ledger (see sql/migrations/001_...) so
inventory_balances is always derived, never hand-edited.

Three steps, all idempotent -- safe to re-run this script as many times
as you want:

  1. Seed one OPENING_BALANCE ledger row per (warehouse, product) from
     whatever's currently in inventory_balances, but ONLY the first time
     (uq_invtxn_opening_balance in the migration blocks duplicates).
  2. Insert clean receiving events into receiving_transactions, and one
     RECEIPT ledger row per event (only accepted units move inventory --
     damaged/rejected units are recorded on the receiving event itself
     for audit purposes, but never enter sellable inventory).
  3. Recompute inventory_balances.quantity_on_hand as
     SUM(quantity_delta) per (warehouse, product) from the full ledger.
     This is a full recompute, not an incremental add -- so it's correct
     no matter how many times this script runs.

Run AFTER run_receiving_validation.py:
    python -m python.validation.run_receiving_validation
    python -m python.etl.load_receiving
"""
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR
from utils.db import get_engine

RECEIVING_QUALITY_LOG_PATH = f"{PROCESSED_DATA_DIR}/receiving_quality_log.csv"


def seed_opening_balances(conn):
    # Guard against ANY existing ledger row for a (warehouse, product) pair --
    # not just an existing OPENING_BALANCE row. inventory_balances itself is
    # NOT a safe guard: recompute_balances() creates a row there for every
    # combo a receipt has ever touched, even ones with no real opening
    # balance, so reading "current" inventory_balances on a later run would
    # mistake an already-derived balance for a fresh opening one and
    # double-count it.
    conn.execute(text("""
        INSERT INTO inventory_transactions
            (warehouse_id, product_id, transaction_type, quantity_delta, notes)
        SELECT ib.warehouse_id, ib.product_id, 'OPENING_BALANCE', ib.quantity_on_hand,
               'Seeded from sql/seed/05_inventory.sql starting balance'
        FROM inventory_balances ib
        WHERE NOT EXISTS (
            SELECT 1 FROM inventory_transactions it
            WHERE it.warehouse_id = ib.warehouse_id AND it.product_id = ib.product_id
        )
        ON CONFLICT (warehouse_id, product_id)
            WHERE transaction_type = 'OPENING_BALANCE' DO NOTHING
    """))


def load_clean_events(conn):
    events_path = Path(RAW_DATA_DIR) / "receiving_events_raw.csv"
    log_path = Path(RECEIVING_QUALITY_LOG_PATH)

    if not events_path.exists():
        sys.exit("Raw receiving events not found. Run generate_receiving_raw.py first.")
    if not log_path.exists():
        sys.exit("Receiving quality log not found. Run run_receiving_validation.py first.")

    events_df = pd.read_csv(events_path)
    issues_df = pd.read_csv(log_path)
    bad_ids = set(issues_df["record_id"])

    events_df["record_id"] = (
        events_df["po_number"] + ":" + events_df["sku"] + ":" + events_df["event_number"].astype(str)
    )
    clean = events_df[~events_df["record_id"].isin(bad_ids)].copy()
    skipped = len(events_df) - len(clean)

    # Resolve po_number/sku to the real po_line_id, and warehouse_code to warehouse_id
    lookup = pd.read_sql("""
        SELECT pol.po_line_id, po.po_number, p.sku
        FROM purchase_order_lines pol
        JOIN purchase_orders po ON po.po_id = pol.po_id
        JOIN products p ON p.product_id = pol.product_id
    """, conn)
    warehouses = pd.read_sql("SELECT warehouse_id, warehouse_code FROM warehouses", conn)

    clean = clean.merge(lookup, on=["po_number", "sku"], how="inner")
    clean = clean.merge(warehouses, on="warehouse_code", how="inner")

    already_loaded = pd.read_sql(
        "SELECT po_line_id, event_number FROM receiving_transactions", conn
    )
    already_key = set(zip(already_loaded["po_line_id"], already_loaded["event_number"]))
    clean = clean[
        ~clean.apply(lambda r: (r["po_line_id"], r["event_number"]) in already_key, axis=1)
    ].reset_index(drop=True)

    product_lookup = pd.read_sql(
        "SELECT po_line_id, product_id FROM purchase_order_lines", conn
    ).set_index("po_line_id")["product_id"].to_dict()

    inserted_count = 0
    for _, row in clean.iterrows():
        result = conn.execute(
            text("""
                INSERT INTO receiving_transactions
                    (po_line_id, warehouse_id, event_number, received_date,
                     quantity_received, quantity_accepted, quantity_damaged, quantity_rejected)
                VALUES
                    (:po_line_id, :warehouse_id, :event_number, :received_date,
                     :quantity_received, :quantity_accepted, :quantity_damaged, :quantity_rejected)
                RETURNING receiving_id
            """),
            {
                "po_line_id": int(row["po_line_id"]),
                "warehouse_id": int(row["warehouse_id"]),
                "event_number": int(row["event_number"]),
                "received_date": row["received_date"],
                "quantity_received": int(row["quantity_received"]),
                "quantity_accepted": int(row["quantity_accepted"]),
                "quantity_damaged": int(row["quantity_damaged"]),
                "quantity_rejected": int(row["quantity_rejected"]),
            },
        )
        receiving_id = result.scalar_one()
        inserted_count += 1

        accepted = int(row["quantity_accepted"])
        if accepted > 0:
            conn.execute(
                text("""
                    INSERT INTO inventory_transactions
                        (warehouse_id, product_id, transaction_type, quantity_delta,
                         reference_receiving_id, notes)
                    VALUES
                        (:warehouse_id, :product_id, 'RECEIPT', :quantity_delta,
                         :receiving_id, 'Auto-generated from receiving_transactions')
                """),
                {
                    "warehouse_id": int(row["warehouse_id"]),
                    "product_id": int(product_lookup[int(row["po_line_id"])]),
                    "quantity_delta": accepted,
                    "receiving_id": receiving_id,
                },
            )

    return inserted_count, skipped


def recompute_balances(conn):
    conn.execute(text("""
        INSERT INTO inventory_balances (warehouse_id, product_id, quantity_on_hand)
        SELECT warehouse_id, product_id, SUM(quantity_delta)
        FROM inventory_transactions
        GROUP BY warehouse_id, product_id
        ON CONFLICT (warehouse_id, product_id)
        DO UPDATE SET quantity_on_hand = EXCLUDED.quantity_on_hand,
                      last_count_date = CURRENT_TIMESTAMP
    """))


def main():
    engine = get_engine()
    with engine.begin() as conn:
        seed_opening_balances(conn)
        inserted, skipped = load_clean_events(conn)
        recompute_balances(conn)

    print(f"Loaded {inserted} clean receiving events ({skipped} skipped for data quality issues).")
    print("Recomputed inventory_balances from the full ledger.")


if __name__ == "__main__":
    main()