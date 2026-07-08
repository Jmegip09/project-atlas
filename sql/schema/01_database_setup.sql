-- ============================================================================
-- PROJECT ATLAS: Enterprise Supply Chain Intelligence Platform
-- Component: sql/schema/01_database_setup.sql (Base Tables & Data Types)
-- Description: Establishes base relational database tables and core columns.
-- ============================================================================

DROP TABLE IF EXISTS receiving_transactions CASCADE;
DROP TABLE IF EXISTS purchase_order_lines CASCADE;
DROP TABLE IF EXISTS purchase_orders CASCADE;
DROP TABLE IF EXISTS inventory_balances CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;


-- 1. SUPPLIERS MASTER TABLE
CREATE TABLE suppliers (
    supplier_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    contact_email VARCHAR(100),
    lead_time_days INT DEFAULT 7,
    supplier_status VARCHAR(20) DEFAULT 'Active'
);

-- 2. PRODUCTS MASTER TABLE
CREATE TABLE products (
    product_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku VARCHAR(50) NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50),
    unit_of_measure VARCHAR(10) DEFAULT 'EA',
    safety_stock_level INT DEFAULT 0
);

-- 3. WAREHOUSES MASTER TABLE
CREATE TABLE warehouses (
    warehouse_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    warehouse_code VARCHAR(10) NOT NULL,
    warehouse_name VARCHAR(100) NOT NULL,
    location_city VARCHAR(100) NOT NULL
);

-- 4. PURCHASE ORDERS TRANSACTION HEADER
CREATE TABLE purchase_orders (
    po_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    po_number VARCHAR(50) NOT NULL,
    supplier_id INT NOT NULL,

    expected_delivery_date DATE,
    po_status VARCHAR(20) DEFAULT 'Open',
    created_by_employee_id INT
);

-- 5. PURCHASE ORDER LINES TRANSACTION DETAILS
CREATE TABLE purchase_order_lines (
    po_line_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    po_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity_ordered INT NOT NULL,
    quantity_received INT NOT NULL DEFAULT 0,
    unit_cost DECIMAL(10, 2) NOT NULL
);

-- 6. INVENTORY BALANCES MASTER RECORDS
CREATE TABLE inventory_balances (
    inventory_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity_on_hand INT DEFAULT 0,
    bin_location VARCHAR(20),
    last_count_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. RECEIVING TRANSACTIONS (Granular Shipment Ingestion)
CREATE TABLE receiving_transactions (
    receiving_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    po_line_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity_received INT NOT NULL,
    received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   received_by_employee_id INT
);

-- 8. DEPARTMENTS MASTER
CREATE TABLE departments (
    department_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_type VARCHAR(50),
    department_status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. EMPLOYEES MASTER
CREATE TABLE employees (
    employee_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_number VARCHAR(25) NOT NULL UNIQUE,
    first_name VARCHAR(75) NOT NULL,
    last_name VARCHAR(75) NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    warehouse_id INT,
    employee_status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


