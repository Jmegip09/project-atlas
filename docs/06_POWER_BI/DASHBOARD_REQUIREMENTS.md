# Power BI Dashboard Requirements

## Purpose

This document defines the current Power BI reporting scope for Project Atlas and the acceptance criteria for version 0.6. It replaces the earlier five-dashboard concept with the three-page report implemented in `powerbi/ProjectAtlas.pbix`.

The dashboard is a presentation layer over validated PostgreSQL reporting views. It must not recreate operational joins or invent metrics that the current data model cannot support.

---

## Report Scope

| Page | Reporting View | Primary Audience | Primary Decision |
|---|---|---|---|
| Supplier Scorecard | `vw_supplier_performance` | Procurement and supply chain leadership | Which suppliers create planning or spend concentration risk? |
| Inventory Risk | `vw_inventory_status` | Inventory control and warehouse operations | Which warehouse-SKU positions require replenishment attention? |
| Receiving & Quality | `vw_receiving_performance` | Warehouse operations and procurement | Where are receipts late, damaged, or rejected? |

Each page uses one reporting view. Cross-page relationships are not required for version 0.6.

---

## Design Principles

The report shall:

- Use reporting views from `sql/views/` as its only data sources.
- Preserve the grain documented in `docs/04_SQL/VIEWS.md`.
- Use KPI definitions from `KPI_CATALOG.md`.
- Prefer explicit measures for cards and reusable calculations.
- Apply business-friendly titles while retaining snake-case source names in the data model.
- Make risk and exception states visually distinct without relying on color alone.
- Use sortable detail tables so every summary can be investigated.
- Avoid presenting planned lead-time variance as actual delivery performance.

---

## Page 1 — Supplier Scorecard

### Purpose

Compare supplier purchasing volume, planned lead time, and purchase order value.

### Business Questions

- How many suppliers are represented?
- Which suppliers have planned lead times above their quoted lead time?
- Which suppliers carry the largest purchase order value?
- Which suppliers have no current purchase order activity?

### Required Visuals

| Visual | Definition | Acceptance Criteria | Current State |
|---|---|---|---|
| Card — Total Suppliers | Distinct count of `supplier_id` | Includes suppliers with zero purchase orders | Not yet implemented |
| Card — Average Supplier Lead-Time Variance | Average of `avg_days_over_quoted_lead_time` | Labeled as an unweighted supplier average, formatted to one decimal day | Not yet implemented |
| Horizontal bar chart | `avg_days_over_quoted_lead_time` by `supplier_name` | Average aggregation; sorted highest to lowest; title states "planned" or "quoted" lead-time variance | Implemented |
| Supplier detail table | Supplier name, status, quoted lead time, total POs, average planned lead time, variance, and PO value | Currency and day formatting applied; sortable by every visible column | Partially implemented — supplier status is not displayed |

### Interpretation Guardrail

This page does not measure actual on-time delivery. Its lead-time metric compares purchase order planning dates with supplier master-data lead time. Actual receipt timing belongs on the Receiving & Quality page.

---

## Page 2 — Inventory Risk

### Purpose

Identify current warehouse-product balances at or below their defined safety-stock level.

### Business Questions

- How many warehouse-SKU positions are at stockout risk?
- Which products have the largest safety-stock shortfall?
- Which warehouses contain the greatest concentration of at-risk positions?
- How much inventory is currently available at each warehouse?

### Required Visuals

| Visual | Definition | Acceptance Criteria | Current State |
|---|---|---|---|
| Card — At-Risk Warehouse-SKU Locations | Count of rows where `is_at_stockout_risk = TRUE` | Uses a warehouse-SKU label unless changed to a distinct SKU count | Implemented; current title should be made more precise |
| At-risk detail table | Warehouse, product, SKU, quantity on hand, safety stock, and units above safety stock | Filtered to `TRUE`; sorted by `units_above_safety_stock` ascending so the deepest shortfall appears first | Partially implemented — risk filter is present; the required shortfall sort is not encoded |
| Bar chart — At-Risk Locations by Warehouse | Count of at-risk warehouse-product rows by `warehouse_name` | Filtered to `TRUE`; sorted highest to lowest | Needs adjustment — current visual shows quantity on hand split by risk flag |

### Interpretation Guardrail

`is_at_stockout_risk` is a safety-stock threshold flag. It is not a forecasted stockout probability and does not account for demand, open purchase orders, or transfer inventory.

---

## Page 3 — Receiving & Quality

### Purpose

Monitor receipt volume, delivery timing, and inspection outcomes by warehouse and supplier.

### Business Questions

- How many receipt events occurred?
- Are receipts arriving before or after their expected delivery date?
- Which warehouses record the most late receiving events?
- Which suppliers account for damaged or rejected units?

### Required Visuals

| Visual | Definition | Acceptance Criteria | Current State |
|---|---|---|---|
| Card — Receiving Events | Count of `receiving_id` | Labeled as events, not purchase orders | Implemented |
| Card — Average Delivery Variance | Average of `days_late` | Positive is late, negative is early; formatted to one decimal day | Implemented in the same card visual |
| Bar chart — Late Receiving Events by Warehouse | Count of receiving rows where `days_late > 0`, grouped by `warehouse_name` | Late-event filter applied; sorted highest to lowest | Needs adjustment — current visual counts all receiving events |
| Stacked bar chart — Receipt Quality by Supplier | Sum of accepted, damaged, and rejected quantities by `supplier_name` | Uses consistent outcome colors and whole-number labels | Implemented |

### Quantity Reconciliation

For every filter context:

```text
Gross Received Units = Accepted Units + Damaged Units + Rejected Units
```

Only accepted units enter sellable inventory. The dashboard should never combine gross received units and accepted units as though they were additive measures.

---

## Filters and Interactions

Version 0.6 should support filtering where the source view contains the field:

- Supplier name
- Supplier status
- Warehouse name
- Location city
- Product category
- SKU
- Expected delivery date
- Received date

Visual selections should cross-filter visuals on the same page. Because the report uses one independent view per page, filters are page-scoped unless a future semantic model introduces shared dimensions.

---

## Formatting Standards

| Data Type | Standard |
|---|---|
| Counts and quantities | Whole numbers with thousands separators |
| Currency | U.S. dollars with thousands separators and no unnecessary decimals |
| Day variance | One decimal place; preserve negative values for early performance |
| Percentages | One decimal place |
| Boolean risk | Display as business labels such as `At Risk` and `Above Safety Stock` |
| Dates | Consistent short-date format |

Risk colors should remain consistent across the report. Red indicates an exception or adverse result, amber indicates attention, and neutral/blue indicates context or acceptable performance. Text labels and sort order must carry the meaning when colors are not distinguishable.

---

## Data Refresh and Validation

Before refreshing Power BI:

1. Run both validation stages and confirm their quality logs exist.
2. Load clean purchase order and receiving data.
3. Recompute `inventory_balances` from `inventory_transactions` through `load_receiving.py`.
4. Confirm all three reporting views return rows.

After refresh, validate:

- Supplier totals against `vw_supplier_performance`.
- At-risk location count against `vw_inventory_status` filtered to `TRUE`.
- Receipt counts and quantity reconciliation against `vw_receiving_performance`.
- No visual is using an unintended implicit aggregation.
- Early receipts are not mislabeled as zero-day or late receipts.

---

## Version 0.6 Acceptance Criteria

The Power BI phase is complete when:

- All three pages refresh without schema or credential errors.
- Every required visual is implemented and correctly labeled.
- Every item marked not implemented, partially implemented, or needing adjustment in the current-state tables is resolved.
- KPI results reconcile to PostgreSQL.
- Dashboard screenshots are added to the repository for portfolio review.
- README, changelog, release notes, and version history are updated to v0.6.0.

Metrics requiring unimplemented entities—such as inventory turnover, cycle-count variance, warehouse utilization, and true demand-based stockout rate—remain outside version 0.6.

---

## Traceability

| Dashboard Page | Reporting Contract | Primary Business Rules |
|---|---|---|
| Supplier Scorecard | `vw_supplier_performance` | `ATLAS-RULE-001`, `ATLAS-RULE-015` |
| Inventory Risk | `vw_inventory_status` | `ATLAS-RULE-007`, `ATLAS-RULE-008`, `ATLAS-RULE-009`, `ATLAS-RULE-015` |
| Receiving & Quality | `vw_receiving_performance` | `ATLAS-RULE-004`, `ATLAS-RULE-005`, `ATLAS-RULE-006`, `ATLAS-RULE-015` |

Data quality rules and rejected-row handling are documented in `docs/05_ETL/DATA_QUALITY_RULES.md`.