-- ============================================================================
-- PROJECT ATLAS: Reporting View
-- Purpose: Single flat table for Power BI's Executive Inventory Dashboard.
-- Grain: one row per warehouse/product combination.
-- ============================================================================

CREATE OR REPLACE VIEW vw_inventory_status AS
SELECT
    w.warehouse_id,
    w.warehouse_name,
    w.location_city,
    p.product_id,
    p.sku,
    p.product_name,
    p.category,
    ib.quantity_on_hand,
    p.safety_stock_level,
    (ib.quantity_on_hand - p.safety_stock_level) AS units_above_safety_stock,
    (ib.quantity_on_hand <= p.safety_stock_level) AS is_at_stockout_risk,
    ib.bin_location,
    ib.last_count_date
FROM inventory_balances ib
JOIN warehouses w ON w.warehouse_id = ib.warehouse_id
JOIN products p ON p.product_id = ib.product_id;