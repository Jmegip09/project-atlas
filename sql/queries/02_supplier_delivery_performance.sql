-- ============================================================================
-- PROJECT ATLAS: Analytical Query
-- Business Question: Which suppliers consistently deliver late, and which
-- have the strongest delivery performance?
-- Logic: Compares each supplier's stated lead_time_days against the actual
-- gap between order_date and expected_delivery_date on their POs. This is a
-- proxy metric until receiving_transactions (actual receipt dates) are
-- populated -- at that point this should be rebuilt on actual vs. expected,
-- not expected vs. quoted lead time.
-- ============================================================================

SELECT
    s.supplier_name,
    s.lead_time_days AS quoted_lead_time_days,
    COUNT(po.po_id) AS total_purchase_orders,
    ROUND(AVG(po.expected_delivery_date - po.order_date), 1) AS avg_planned_lead_time_days,
    ROUND(
        AVG(po.expected_delivery_date - po.order_date) - s.lead_time_days,
        1
    ) AS avg_days_over_quoted_lead_time
FROM purchase_orders po
JOIN suppliers s ON s.supplier_id = po.supplier_id
GROUP BY s.supplier_name, s.lead_time_days
ORDER BY avg_days_over_quoted_lead_time DESC;