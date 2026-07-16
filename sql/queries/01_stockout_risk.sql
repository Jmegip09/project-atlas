-- ============================================================================
-- PROJECT ATLAS: Analytical Query
-- Business Question: Which products are at risk of stockout?
-- Logic: A product is at risk if its on-hand quantity at a warehouse has
-- fallen to or below its defined safety stock level.
-- ============================================================================

SELECT
    w.warehouse_name,
    p.product_name,
    p.sku,
    ib.quantity_on_hand,
    p.safety_stock_level,
    (p.safety_stock_level - ib.quantity_on_hand) AS units_below_safety_stock
FROM inventory_balances ib
JOIN products p ON p.product_id = ib.product_id
JOIN warehouses w ON w.warehouse_id = ib.warehouse_id
WHERE ib.quantity_on_hand <= p.safety_stock_level
ORDER BY units_below_safety_stock DESC;