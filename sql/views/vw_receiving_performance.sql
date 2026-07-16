-- ============================================================================
-- PROJECT ATLAS: Reporting View
-- Purpose: Single flat table for Power BI's Warehouse Operations Dashboard.
-- Grain: one row per receiving transaction.
-- ============================================================================

CREATE OR REPLACE VIEW vw_receiving_performance AS
SELECT
    rt.receiving_id,
    rt.event_number,
    w.warehouse_id,
    w.warehouse_name,
    w.location_city,
    po.po_number,
    s.supplier_name,
    p.sku,
    p.product_name,
    rt.quantity_received,
    rt.quantity_accepted,
    rt.quantity_damaged,
    rt.quantity_rejected,
    po.expected_delivery_date,
    rt.received_date,
    (rt.received_date::date - po.expected_delivery_date) AS days_late
FROM receiving_transactions rt
JOIN warehouses w ON w.warehouse_id = rt.warehouse_id
JOIN purchase_order_lines pol ON pol.po_line_id = rt.po_line_id
JOIN purchase_orders po ON po.po_id = pol.po_id
JOIN suppliers s ON s.supplier_id = po.supplier_id
JOIN products p ON p.product_id = pol.product_id;