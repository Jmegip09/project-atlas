# KPI Catalog

## Purpose

This catalog defines the metrics used by the current Project Atlas Power BI report. It establishes one business definition, source, grain, and interpretation for each KPI so visual labels do not overstate what the underlying data proves.

SQL view names and columns use lowercase snake case. The current Power BI model exposes each imported table with its PostgreSQL schema prefix, such as `'public vw_inventory_status'`; the DAX examples use those exact model names. Power BI measure names use title case for business readability.

---

## Status Definitions

| Status | Meaning |
|---|---|
| Implemented | The metric is available in `powerbi/ProjectAtlas.pbix`. |
| Available | The reporting view supports the metric, but the required visual or explicit measure is not complete. |
| Proposed | Additional SQL or model work is required before the metric can be reported reliably. |

---

## Supplier Scorecard KPIs

### ATLAS-KPI-001 — Total Suppliers

| Attribute | Definition |
|---|---|
| Status | Available |
| Source | `vw_supplier_performance` |
| Grain | Supplier |
| Calculation | Count of `supplier_id` |
| Format | Whole number |
| Interpretation | Number of suppliers represented in the reporting view, including suppliers with no purchase orders. |

Suggested measure:

```DAX
Total Suppliers =
DISTINCTCOUNT('public vw_supplier_performance'[supplier_id])
```

### ATLAS-KPI-002 — Average Supplier Lead-Time Variance

| Attribute | Definition |
|---|---|
| Status | Implemented as a supplier comparison; summary card remains available |
| Source | `vw_supplier_performance.avg_days_over_quoted_lead_time` |
| Grain | Supplier |
| Calculation | Average of supplier-level planned lead-time variance |
| Format | `0.0 days` |
| Interpretation | Positive values indicate planned delivery windows exceeding quoted supplier lead time. Negative values indicate planned windows inside quoted lead time. |

Suggested measure:

```DAX
Average Supplier Lead-Time Variance =
AVERAGE('public vw_supplier_performance'[avg_days_over_quoted_lead_time])
```

This is an unweighted average of supplier averages. It is not a true company-wide purchase-order-weighted average and it is not actual delivery delay. A weighted company KPI requires purchase-order-level rows or an additional SQL calculation.

### ATLAS-KPI-003 — Total Purchase Orders

| Attribute | Definition |
|---|---|
| Status | Implemented in the supplier table |
| Source | `vw_supplier_performance.total_purchase_orders` |
| Grain | Supplier |
| Calculation | Sum of distinct purchase-order counts by supplier |
| Format | Whole number |
| Interpretation | Total purchase orders represented across suppliers. |

### ATLAS-KPI-004 — Total Purchase Order Value

| Attribute | Definition |
|---|---|
| Status | Implemented in the supplier table |
| Source | `vw_supplier_performance.total_po_value` |
| Grain | Supplier |
| Calculation | Sum of `quantity_ordered * unit_cost` |
| Format | Currency |
| Interpretation | Original value of ordered units; it is not received value, outstanding value, or invoice spend. |

---

## Inventory Risk KPIs

### ATLAS-KPI-005 — At-Risk Warehouse-SKU Locations

| Attribute | Definition |
|---|---|
| Status | Implemented |
| Source | `vw_inventory_status` |
| Grain | Warehouse-product |
| Calculation | Count of rows where `is_at_stockout_risk = TRUE` |
| Format | Whole number |
| Interpretation | Number of warehouse-SKU positions at or below safety stock. |

Suggested measure:

```DAX
At-Risk Warehouse-SKU Locations =
CALCULATE(
    COUNTROWS('public vw_inventory_status'),
    'public vw_inventory_status'[is_at_stockout_risk] = TRUE()
)
```

The current card title, "Products at Stockout Risk," can imply a distinct product count. Unless the calculation changes to `DISTINCTCOUNT(sku)`, the more precise label is "At-Risk Warehouse-SKU Locations."

### ATLAS-KPI-006 — Quantity on Hand

| Attribute | Definition |
|---|---|
| Status | Implemented |
| Source | `vw_inventory_status.quantity_on_hand` |
| Grain | Warehouse-product |
| Calculation | Sum of current on-hand units in the selected filter context |
| Format | Whole number |
| Interpretation | Current sellable inventory derived from opening balances and accepted receipt ledger movements. |

### ATLAS-KPI-007 — Units Above Safety Stock

| Attribute | Definition |
|---|---|
| Status | Implemented |
| Source | `vw_inventory_status.units_above_safety_stock` |
| Grain | Warehouse-product |
| Calculation | `quantity_on_hand - safety_stock_level` |
| Format | Whole number |
| Interpretation | Positive values show buffer stock; `0` is at the threshold; negative values show the shortfall. |

Do not aggregate this field across warehouses as a company risk measure without careful labeling. Surplus at one location can hide a shortage at another.

---

## Receiving & Quality KPIs

### ATLAS-KPI-008 — Receiving Events

| Attribute | Definition |
|---|---|
| Status | Implemented |
| Source | `vw_receiving_performance.receiving_id` |
| Grain | Receiving event |
| Calculation | Count of `receiving_id` |
| Format | Whole number |
| Interpretation | Number of receipt events, not distinct purchase orders or purchase order lines. Partial receipts increase the event count. |

### ATLAS-KPI-009 — Average Delivery Variance

| Attribute | Definition |
|---|---|
| Status | Implemented |
| Source | `vw_receiving_performance.days_late` |
| Grain | Receiving event |
| Calculation | Average of `days_late` across all selected events |
| Format | `0.0 days` |
| Interpretation | Average timing versus the expected delivery date. Positive is late; negative is early. |

The current metric includes early and on-time events. Label it "Average Delivery Variance," not "Average Days Late." If the business needs average lateness only, filter to `days_late > 0`.

### ATLAS-KPI-010 — Late Receiving Events

| Attribute | Definition |
|---|---|
| Status | Available |
| Source | `vw_receiving_performance` |
| Grain | Receiving event |
| Calculation | Count of rows where `days_late > 0` |
| Format | Whole number |
| Interpretation | Receipt events recorded after the purchase order's expected delivery date. |

Suggested measure:

```DAX
Late Receiving Events =
CALCULATE(
    COUNTROWS('public vw_receiving_performance'),
    'public vw_receiving_performance'[days_late] > 0
)
```

### ATLAS-KPI-011 — Accepted Units

| Attribute | Definition |
|---|---|
| Status | Implemented |
| Source | `vw_receiving_performance.quantity_accepted` |
| Calculation | Sum of accepted units |
| Interpretation | Units that passed inspection and were eligible to increase sellable inventory. |

### ATLAS-KPI-012 — Damaged Units

| Attribute | Definition |
|---|---|
| Status | Implemented |
| Source | `vw_receiving_performance.quantity_damaged` |
| Calculation | Sum of damaged units |
| Interpretation | Units recorded as damaged and excluded from sellable inventory. |

### ATLAS-KPI-013 — Rejected Units

| Attribute | Definition |
|---|---|
| Status | Implemented |
| Source | `vw_receiving_performance.quantity_rejected` |
| Calculation | Sum of rejected units |
| Interpretation | Units rejected during inspection and excluded from sellable inventory. |

### ATLAS-KPI-014 — Receipt Exception Rate

| Attribute | Definition |
|---|---|
| Status | Available |
| Source | `vw_receiving_performance` |
| Calculation | `(damaged units + rejected units) / gross received units` |
| Format | Percentage, one decimal place |
| Interpretation | Share of physically received units that did not enter sellable inventory. |

Suggested measure:

```DAX
Receipt Exception Rate =
DIVIDE(
    SUM('public vw_receiving_performance'[quantity_damaged])
        + SUM('public vw_receiving_performance'[quantity_rejected]),
    SUM('public vw_receiving_performance'[quantity_received])
)
```

---

## Metrics Not Yet Supported

The following metrics appear in older planning documents but cannot be calculated reliably from the current reporting model:

- Inventory accuracy percentage
- Inventory turnover
- True stockout rate based on demand
- Warehouse utilization
- Cycle-count variance
- Inventory aging
- Actual supplier on-time delivery percentage at purchase-order grain

These metrics require additional business events, dimensional context, or reporting views. They should remain out of the dashboard until their data contracts are implemented.

---

## Metric Governance

Before adding or changing a KPI:

- Confirm its business question and decision owner.
- State the metric grain before writing the calculation.
- Prefer explicit DAX measures over implicit visual aggregations.
- Reconcile totals against the source SQL view.
- Update this catalog, `DASHBOARD_REQUIREMENTS.md`, and the changelog together.
- Avoid labels such as "rate," "on-time," or "company-wide" unless the denominator and weighting are explicitly defined.