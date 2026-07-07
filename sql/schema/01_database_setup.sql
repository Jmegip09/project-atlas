-- ============================================================================
-- PROJECT ATLAS: Enterprise Supply Chain Intelligence Platform
-- Component: 01_database_setup.sql (Data Definition Language - DDL)
-- Description: Initializes the foundational relational model with strict 
--              referential integrity constraints and enterprise validation rules.
-- Status: Prototype / Subject to change after business process mapping
-- ============================================================================

-- Drop tables if they exist to ensure clean deployment idempotency
DROP TABLE IF EXISTS purchase_order_lines CASCADE;
DROP TABLE IF EXISTS purchase_orders CASCADE;
DROP TABLE IF EXISTS inventory_balances CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;

-- 1. SUPPLIERS MASTER
CREATE TABLE suppliers (
    supplier_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL UNIQUE,
    contact_email VARCHAR(100),
    lead_time_days INT DEFAULT 7 CHECK (lead_time_days >= 0),
    supplier_status VARCHAR(20) DEFAULT 'Active' CHECK (supplier_status IN ('Active', 'On Hold', 'Inactive'))
);

-- 2. PRODUCTS MASTER (Evolved Core Catalog)
CREATE TABLE products (
    product_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50),
    unit_of_measure VARCHAR(10) DEFAULT 'EA',
    safety_stock_level INT DEFAULT 0 CHECK (safety_stock_level >= 0)
);

-- 3. WAREHOUSES MASTER
CREATE TABLE warehouses (
    warehouse_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    warehouse_code VARCHAR(10) NOT NULL UNIQUE,
    warehouse_name VARCHAR(100) NOT NULL,
    location_city VARCHAR(100) NOT NULL
);

-- 4. PURCHASE ORDERS (PO Headers)
CREATE TABLE purchase_orders (
    po_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    po_number VARCHAR(50) NOT NULL UNIQUE,
    supplier_id INT NOT NULL REFERENCES suppliers(supplier_id) ON DELETE RESTRICT,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_delivery_date DATE,
    po_status VARCHAR(20) DEFAULT 'Open' CHECK (po_status IN ('Open', 'Partially Received', 'Fully Received', 'Cancelled')),
    CONSTRAINT chk_delivery_date CHECK (expected_delivery_date >= order_date)
);

-- 5. PURCHASE ORDER LINES (PO Details)
CREATE TABLE purchase_order_lines (
    po_line_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    po_id INT NOT NULL REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity_ordered INT NOT NULL CHECK (quantity_ordered > 0),
-- TODO: Replace quantity_received with receiving table in next schema revision
    quantity_received INT DEFAULT 0 CHECK (quantity_received >= 0),
    unit_cost DECIMAL(10, 2) NOT NULL CHECK (unit_cost >= 0),
    CONSTRAINT chk_received_qty CHECK (quantity_received <= quantity_ordered)
);

-- 6. INVENTORY LEDGER (Real-Time Balances)
CREATE TABLE inventory_balances (
    inventory_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    warehouse_id INT NOT NULL REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity_on_hand INT DEFAULT 0 CHECK (quantity_on_hand >= 0),
    bin_location VARCHAR(20),
    last_count_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_warehouse_product UNIQUE (warehouse_id, product_id)
);

-- ============================================================================
-- PERFORMANCE & REPORTING OPTIMIZATION (Indexes)
-- ============================================================================
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_po_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_pol_po ON purchase_order_lines(po_id);
CREATE INDEX idx_inventory_lookup ON inventory_balances(warehouse_id, product_id);
