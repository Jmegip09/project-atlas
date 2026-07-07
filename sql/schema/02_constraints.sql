-- ============================================================================
-- PROJECT ATLAS: Enterprise Supply Chain Intelligence Platform
-- Component: sql/schema/02_constraints.sql (Data Integrity & Business Rules)
-- Description: Enforces strict data quality, uniqueness constraints, and 
--              referential integrity across all system entities.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- UNIQUE CONSTRAINTS (Preventing Duplicate Data Records)
-- ----------------------------------------------------------------------------
ALTER TABLE inventory_balances ADD CONSTRAINT uq_warehouse_product UNIQUE (warehouse_id, product_id);
ALTER TABLE inventory_balances ADD CONSTRAINT fk_balances_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT;
ALTER TABLE inventory_balances ADD CONSTRAINT fk_balances_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT;
ALTER TABLE inventory_balances ADD CONSTRAINT chk_qty_on_hand CHECK (quantity_on_hand >= 0);

-- ----------------------------------------------------------------------------
-- FOREIGN KEY CONSTRAINTS (Referential Integrity Guardrails)
-- ----------------------------------------------------------------------------

-- Link Purchase Orders to a Valid Supplier
ALTER TABLE purchase_orders 
    ADD CONSTRAINT fk_po_supplier 
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) 
    ON DELETE RESTRICT;

-- Link PO Lines to Parent Header (Cascade deletes if a whole PO is canceled/dropped)
ALTER TABLE purchase_order_lines 
    ADD CONSTRAINT fk_pol_po 
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id) 
    ON DELETE CASCADE;

-- Link PO Lines to Valid Product SKU
ALTER TABLE purchase_order_lines 
    ADD CONSTRAINT fk_pol_product 
    FOREIGN KEY (product_id) REFERENCES products(product_id) 
    ON DELETE RESTRICT;

-- Link Ledger Records to Valid Warehouse Node
ALTER TABLE inventory_ledger 
    ADD CONSTRAINT fk_ledger_warehouse 
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) 
    ON DELETE RESTRICT;

-- Link Ledger Records to Valid Product SKU
ALTER TABLE inventory_ledger 
    ADD CONSTRAINT fk_ledger_product 
    FOREIGN KEY (product_id) REFERENCES products(product_id) 
    ON DELETE RESTRICT;

-- Link Receiving Events to Valid PO Lines
ALTER TABLE receiving_transactions 
    ADD CONSTRAINT fk_receiving_po_line 
    FOREIGN KEY (po_line_id) REFERENCES purchase_order_lines(po_line_id) 
    ON DELETE RESTRICT;

-- Link Receiving Events to a Valid Warehouse Destination Node
ALTER TABLE receiving_transactions 
    ADD CONSTRAINT fk_receiving_warehouse 
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) 
    ON DELETE RESTRICT;

-- Prevent negative or zero transaction insertions
ALTER TABLE receiving_transactions 
    ADD CONSTRAINT chk_receiving_qty 
    CHECK (quantity_received > 0);

-- ----------------------------------------------------------------------------
-- CHECK CONSTRAINTS (Enterprise Business Rules Validation)
-- ----------------------------------------------------------------------------

-- Supplier Rules
ALTER TABLE suppliers ADD CONSTRAINT chk_supplier_status 
    CHECK (supplier_status IN ('Active', 'On Hold', 'Inactive'));
ALTER TABLE suppliers ADD CONSTRAINT chk_lead_time 
    CHECK (lead_time_days >= 0);

-- Product Rules
ALTER TABLE products ADD CONSTRAINT chk_safety_stock 
    CHECK (safety_stock_level >= 0);

-- Purchase Order Date Logic (Delivery cannot occur before ordering)
ALTER TABLE purchase_orders ADD CONSTRAINT chk_delivery_date 
    CHECK (expected_delivery_date >= order_date);
ALTER TABLE purchase_orders ADD CONSTRAINT chk_po_status 
    CHECK (po_status IN ('Open', 'Partially Received', 'Fully Received', 'Cancelled'));

-- PO Financial & Quantity Guardrails
ALTER TABLE purchase_order_lines ADD CONSTRAINT chk_qty_ordered 
    CHECK (quantity_ordered > 0);
ALTER TABLE purchase_order_lines ADD CONSTRAINT chk_qty_received 
    CHECK (quantity_received >= 0);
ALTER TABLE purchase_order_lines ADD CONSTRAINT chk_unit_cost 
    CHECK (unit_cost >= 0);
ALTER TABLE purchase_order_lines ADD CONSTRAINT chk_received_vs_ordered 
    CHECK (quantity_received <= quantity_ordered);

-- Inventory Ledger Quantity Guardrails (Prevent negative physical inventory)
ALTER TABLE inventory_ledger ADD CONSTRAINT chk_qty_on_hand 
    CHECK (quantity_on_hand >= 0);