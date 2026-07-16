-- ============================================================================
-- PROJECT ATLAS: Migration 001
-- Purpose: Support realistic receiving simulation (partial/damaged/rejected)
-- and a real inventory ledger, instead of a single quantity_received field
-- and a snapshot table nothing ever writes to.
--
-- Design:
--   receiving_transactions gets an event_number (a PO line can be received
--   across multiple shipments) and a quality breakdown per event.
--
--   inventory_transactions is an append-only ledger. inventory_balances
--   stops being hand-maintained and instead always equals
--   SUM(quantity_delta) per (warehouse_id, product_id) -- opening balances
--   from the original seed become one ledger row each, receiving events
--   become RECEIPT rows, and quantity_on_hand is recomputed from the ledger
--   every load run (see load_receiving.py). This makes reloads idempotent:
--   run it once or ten times, the balance is always "opening + everything
--   that's happened since," never "whatever it happened to be plus more."
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. RECEIVING: multi-event support + quality breakdown
-- ----------------------------------------------------------------------------

ALTER TABLE receiving_transactions
    ADD COLUMN event_number INT NOT NULL DEFAULT 1,
    ADD COLUMN quantity_accepted INT NOT NULL DEFAULT 0,
    ADD COLUMN quantity_damaged INT NOT NULL DEFAULT 0,
    ADD COLUMN quantity_rejected INT NOT NULL DEFAULT 0;

ALTER TABLE receiving_transactions
    ADD CONSTRAINT uq_receiving_po_line_event UNIQUE (po_line_id, event_number);

ALTER TABLE receiving_transactions
    ADD CONSTRAINT chk_receiving_quality_breakdown
    CHECK (quantity_accepted + quantity_damaged + quantity_rejected = quantity_received);

ALTER TABLE receiving_transactions
    ADD CONSTRAINT chk_receiving_quality_nonnegative
    CHECK (quantity_accepted >= 0 AND quantity_damaged >= 0 AND quantity_rejected >= 0);

-- ----------------------------------------------------------------------------
-- 2. INVENTORY LEDGER: append-only movement log
-- ----------------------------------------------------------------------------

CREATE TABLE inventory_transactions (
    transaction_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    quantity_delta INT NOT NULL,
    reference_receiving_id INT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR(255)
);

ALTER TABLE inventory_transactions
    ADD CONSTRAINT fk_invtxn_warehouse FOREIGN KEY (warehouse_id)
        REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_invtxn_product FOREIGN KEY (product_id)
        REFERENCES products(product_id) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_invtxn_receiving FOREIGN KEY (reference_receiving_id)
        REFERENCES receiving_transactions(receiving_id) ON DELETE SET NULL,
    ADD CONSTRAINT chk_invtxn_type CHECK (
        transaction_type IN ('OPENING_BALANCE', 'RECEIPT', 'ADJUSTMENT', 'SHIPMENT')
    );

CREATE INDEX idx_invtxn_warehouse_product ON inventory_transactions(warehouse_id, product_id);

-- Prevent seeding an opening balance for the same warehouse/product twice
CREATE UNIQUE INDEX uq_invtxn_opening_balance
    ON inventory_transactions (warehouse_id, product_id)
    WHERE transaction_type = 'OPENING_BALANCE';