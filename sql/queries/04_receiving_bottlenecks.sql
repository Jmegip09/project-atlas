-- ============================================================================
-- PROJECT ATLAS: Analytical Query
-- Business Question: Which warehouses experience receiving bottlenecks?
-- Logic: For each warehouse, compares actual received_date against the
-- PO's expected_delivery_date. A positive avg_days_late means receipts at
-- that warehouse are, on average, arriving after they were expected --
-- a signal of dock/putaway bottlenecks or upstream delivery problems
-- concentrated at that location.
-- ============================================================================

SELECT
    w.warehouse_name,
    w.location_city,
    COUNT(rt.receiving_id) AS total_receipts,
    ROUND(AVG(rt.received_date::date - po.expected_delivery_date), 1) AS avg_days_late,
    COUNT(*) FILTER (WHERE rt.received_date::date > po.expected_delivery_date) AS late_receipt_count
FROM receiving_transactions rt
JOIN warehouses w ON w.warehouse_id = rt.warehouse_id
JOIN purchase_order_lines pol ON pol.po_line_id = rt.po_line_id
JOIN purchase_orders po ON po.po_id = pol.po_id
GROUP BY w.warehouse_name, w.location_city
ORDER BY avg_days_late DESC;
