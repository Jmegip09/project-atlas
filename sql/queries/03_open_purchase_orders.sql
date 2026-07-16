-- ============================================================================
-- PROJECT ATLAS: Analytical Query
-- Business Question: Which purchase orders remain partially received, and
-- what dollar value is still outstanding?
-- ============================================================================

SELECT
    po.po_number,
    s.supplier_name,
    po.po_status,
    po.expected_delivery_date,
    SUM(pol.quantity_ordered) AS total_units_ordered,
    SUM(pol.quantity_received) AS total_units_received,
    SUM(pol.quantity_ordered - pol.quantity_received) AS units_outstanding,
    SUM((pol.quantity_ordered - pol.quantity_received) * pol.unit_cost) AS outstanding_value
FROM purchase_orders po
JOIN suppliers s ON s.supplier_id = po.supplier_id
JOIN purchase_order_lines pol ON pol.po_id = po.po_id
WHERE po.po_status IN ('Open', 'Partially Received')
GROUP BY po.po_number, s.supplier_name, po.po_status, po.expected_delivery_date
ORDER BY outstanding_value DESC;