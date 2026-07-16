-- ============================================================================
-- PROJECT ATLAS: Analytical Query
-- Business Question: Where are inventory discrepancies occurring?
-- Logic: Two discrepancy signals per supplier/product:
--   1. Shortfall: quantity_ordered vs. total ACCEPTED (never made whole even
--      after every receipt logged so far).
--   2. Damage/rejection concentration: what share of gross received units
--      never made it into sellable inventory.
-- ============================================================================

SELECT
    s.supplier_name,
    p.sku,
    p.product_name,
    SUM(pol.quantity_ordered) AS total_ordered,
    SUM(rt.quantity_accepted) AS total_accepted,
    SUM(rt.quantity_damaged) AS total_damaged,
    SUM(rt.quantity_rejected) AS total_rejected,
    SUM(pol.quantity_ordered) - SUM(rt.quantity_accepted) AS shortfall,
    ROUND(
        100.0 * SUM(rt.quantity_damaged + rt.quantity_rejected)
        / NULLIF(SUM(rt.quantity_received), 0), 1
    ) AS pct_never_accepted
FROM purchase_order_lines pol
JOIN purchase_orders po ON po.po_id = pol.po_id
JOIN suppliers s ON s.supplier_id = po.supplier_id
JOIN products p ON p.product_id = pol.product_id
JOIN receiving_transactions rt ON rt.po_line_id = pol.po_line_id
GROUP BY s.supplier_name, p.sku, p.product_name
HAVING SUM(pol.quantity_ordered) - SUM(rt.quantity_accepted) > 0
    OR SUM(rt.quantity_damaged + rt.quantity_rejected) > 0
ORDER BY pct_never_accepted DESC NULLS LAST, shortfall DESC;