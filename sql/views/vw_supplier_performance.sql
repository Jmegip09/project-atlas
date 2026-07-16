-- ============================================================================
-- PROJECT ATLAS: Reporting View
-- Purpose: Single flat table for Power BI's Supplier Performance Dashboard.
-- Grain: one row per supplier.
-- ============================================================================

CREATE OR REPLACE VIEW vw_supplier_performance AS
SELECT
    s.supplier_id,
    s.supplier_name,
    s.supplier_status,
    s.lead_time_days AS quoted_lead_time_days,
    COUNT(DISTINCT po.po_id) AS total_purchase_orders,
    ROUND(AVG(po.expected_delivery_date - po.order_date), 1) AS avg_planned_lead_time_days,
    ROUND(
        AVG(po.expected_delivery_date - po.order_date) - s.lead_time_days, 1
    ) AS avg_days_over_quoted_lead_time,
    SUM(pol.quantity_ordered * pol.unit_cost) AS total_po_value
FROM suppliers s
LEFT JOIN purchase_orders po ON po.supplier_id = s.supplier_id
LEFT JOIN purchase_order_lines pol ON pol.po_id = po.po_id
GROUP BY s.supplier_id, s.supplier_name, s.supplier_status, s.lead_time_days;