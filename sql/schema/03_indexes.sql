-- ============================================================================
-- PROJECT ATLAS: Enterprise Supply Chain Intelligence Platform
-- Component: sql/schema/03_indexes.sql (Performance Optimization Layer)
-- Description: Establishes strategic B-Tree and Composite indexes to accelerate
--              analytical query execution, table joins, and reporting aggregation.
-- ============================================================================

-- Note: PostgreSQL automatically creates unique indexes for PRIMARY KEY and 
-- UNIQUE constraints. The indexes below target columns heavily used in analytical operations.

-- ----------------------------------------------------------------------------
-- 1. MASTER DATA PERFORMANCE OPTIMIZATIONS
-- ----------------------------------------------------------------------------

-- Accelerate product lookups by SKU during data ingestion and validation pipelines
CREATE INDEX idx_products_sku 
    ON products(sku);

-- Optimize warehouse lookups by location city for geographic reporting distribution
CREATE INDEX idx_warehouses_city 
    ON warehouses(location_city);

-- ----------------------------------------------------------------------------
-- 2. TRANSACTIONAL LAYER OPTIMIZATIONS (Foreign Key & Date Lookups)
-- ----------------------------------------------------------------------------

-- Accelerate table joins and supplier metric score-carding on Purchase Orders
CREATE INDEX idx_po_supplier_id 
    ON purchase_orders(supplier_id);

-- Optimize time-series analysis and date-filtering on Purchase Order headers
CREATE INDEX idx_po_order_date 
    ON purchase_orders(order_date);

-- Speed up nested lookups matching granular line items back to parent PO headers
CREATE INDEX idx_pol_po_id 
    ON purchase_order_lines(po_id);

-- Speed up product velocity lookups within purchase order lines
CREATE INDEX idx_pol_product_id 
    ON purchase_order_lines(product_id);

-- ----------------------------------------------------------------------------
-- 3. INVENTORY LEDGER OPTIMIZATIONS (Composite Indexing)
-- ----------------------------------------------------------------------------

-- High-impact Composite Index: Accelerates multi-facility inventory tracking 
-- and real-time stock balance lookups across specific warehouse/product intersections
CREATE INDEX idx_balances_warehouse_product 
    ON inventory_balances(warehouse_id, product_id);


--- ----------------------------------------------------------------------------
-- 4. EMPLOYEES AND DEPARTMENTS
--- ----------------------------------------------------------------------------

CREATE INDEX idx_employees_department
ON employees(department_id);

CREATE INDEX idx_employees_warehouse
ON employees(warehouse_id);

CREATE INDEX idx_departments_type
ON departments(department_type);