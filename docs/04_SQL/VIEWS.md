# Reporting Views

## Purpose

This document defines the PostgreSQL reporting views that form the contract between the Project Atlas operational database and Power BI. Each view exposes a flattened, business-facing dataset with a documented grain so dashboard calculations do not depend on direct joins to transactional tables.

The SQL files in `sql/views/` are the source of truth for implementation. This document explains how those objects should be interpreted and consumed.

---

## Design Standards

Project Atlas reporting views follow these conventions:

- View names use lowercase snake case and the `vw_` prefix.
- Each view has one declared grain and must not mix aggregation levels.
- Business-facing names are preferred over database implementation details.
- Power BI connects to reporting views rather than rebuilding operational joins.
- Derived columns are calculated consistently in PostgreSQL and reused by every report consumer.
- A view may expose identifiers for traceability, but dashboards should display descriptive business fields by default.

---

## View Catalog

| View | Grain | Primary Consumer | SQL Definition |
|---|---|---|---|
| `vw_supplier_performance` | One row per supplier | Supplier Scorecard | `sql/views/vw_supplier_performance.sql` |
| `vw_inventory_status` | One row per warehouse-product balance | Inventory Risk | `sql/views/vw_inventory_status.sql` |
| `vw_receiving_performance` | One row per receiving event | Receiving & Quality | `sql/views/vw_receiving_performance.sql` |

---

## `vw_supplier_performance`

### Business Purpose

Provides a supplier-level scorecard for purchasing volume, planned lead time, and purchase order value.

### Grain

One row per supplier, including suppliers with no purchase orders because the view uses left joins from `suppliers`.

### Source Tables

- `suppliers`
- `purchase_orders`
- `purchase_order_lines`

### Columns

| Column | Definition |
|---|---|
| `supplier_id` | Surrogate identifier for the supplier. |
| `supplier_name` | Supplier business name. |
| `supplier_status` | Current supplier status. |
| `quoted_lead_time_days` | Standard lead time recorded in supplier master data. |
| `total_purchase_orders` | Distinct count of purchase order headers for the supplier. |
| `avg_planned_lead_time_days` | Average number of days between `order_date` and `expected_delivery_date`. |
| `avg_days_over_quoted_lead_time` | Average planned lead time minus the supplier's quoted lead time. Positive values indicate plans exceeding the quoted lead time; negative values indicate plans inside it. |
| `total_po_value` | Sum of `quantity_ordered * unit_cost` across the supplier's purchase order lines. |

### Interpretation Boundary

`avg_days_over_quoted_lead_time` measures planning variance, not actual delivery performance. It compares expected delivery dates with quoted lead time and does not use `receiving_transactions.received_date`. It must not be labeled "on-time delivery" or "average delivery delay."

Suppliers without purchase orders return `0` for `total_purchase_orders` and may return `NULL` for the average and value fields.

---

## `vw_inventory_status`

### Business Purpose

Provides the current inventory position and safety-stock risk for each stocked product at each warehouse.

### Grain

One row per warehouse-product record in `inventory_balances`.

### Source Tables

- `inventory_balances`
- `warehouses`
- `products`

### Columns

| Column | Definition |
|---|---|
| `warehouse_id` | Surrogate identifier for the warehouse. |
| `warehouse_name` | Warehouse business name. |
| `location_city` | City in which the warehouse operates. |
| `product_id` | Surrogate identifier for the product. |
| `sku` | Product stock-keeping unit. |
| `product_name` | Product business name. |
| `category` | Product category. |
| `quantity_on_hand` | Current quantity derived from the inventory transaction ledger. |
| `safety_stock_level` | Minimum inventory threshold defined for the product. |
| `units_above_safety_stock` | `quantity_on_hand - safety_stock_level`; negative values show the size of the shortfall. |
| `is_at_stockout_risk` | `TRUE` when quantity on hand is equal to or below safety stock. |
| `bin_location` | Warehouse storage location when populated. |
| `last_count_date` | Timestamp last written to the balance record. During ledger recomputation this is the recomputation timestamp, not necessarily a physical cycle-count date. |

### Interpretation Boundary

The risk flag describes a warehouse-product position, not a unique product across the company. A SKU below safety stock in two warehouses represents two at-risk positions. The flag is threshold-based and does not incorporate demand forecasts, open purchase orders, or projected consumption.

---

## `vw_receiving_performance`

### Business Purpose

Provides event-level receiving, delivery timing, and quality results for warehouse and supplier analysis.

### Grain

One row per `receiving_transactions` record. A purchase order line can produce multiple rows when it is received across multiple events.

### Source Tables

- `receiving_transactions`
- `purchase_order_lines`
- `purchase_orders`
- `suppliers`
- `products`
- `warehouses`

### Columns

| Column | Definition |
|---|---|
| `receiving_id` | Surrogate identifier for the receiving event. |
| `event_number` | Sequence number of the event within a purchase order line. |
| `warehouse_id` | Warehouse receiving the shipment. |
| `warehouse_name` | Warehouse business name. |
| `location_city` | Warehouse city. |
| `po_number` | Purchase order business identifier. |
| `supplier_name` | Supplier associated with the purchase order. |
| `sku` | Product stock-keeping unit. |
| `product_name` | Product business name. |
| `quantity_received` | Gross units recorded at the dock. |
| `quantity_accepted` | Units accepted into sellable inventory. |
| `quantity_damaged` | Units identified as damaged. |
| `quantity_rejected` | Units rejected during inspection. |
| `expected_delivery_date` | Expected delivery date from the purchase order. |
| `received_date` | Timestamp of the receiving event. |
| `days_late` | Calendar-day difference between receipt date and expected delivery date. Positive values are late, `0` is on the expected date, and negative values are early. |

### Quantity Reconciliation

Every clean receiving event must satisfy:

```text
quantity_received = quantity_accepted + quantity_damaged + quantity_rejected
```

Only `quantity_accepted` creates a `RECEIPT` movement in `inventory_transactions`. Damaged and rejected units remain visible for quality analysis but do not increase sellable inventory.

---

## Deployment Order

Create the reporting views after the base schema and receiving migration have been applied:

```bash
psql -d your_db -f sql/views/vw_supplier_performance.sql
psql -d your_db -f sql/views/vw_inventory_status.sql
psql -d your_db -f sql/views/vw_receiving_performance.sql
```

The views can be created before transactional data is loaded, but Power BI will remain empty until the ETL pipeline has populated the underlying tables.

---

## Change Control

Any change to a reporting view must include:

- An explicit review of the view's grain.
- A check for duplicate amplification after joins.
- A corresponding update to `KPI_CATALOG.md` and `DASHBOARD_REQUIREMENTS.md`.
- A Power BI refresh to confirm column names and data types remain compatible.
- A changelog entry when the reporting contract changes.

Removing or renaming an exposed column is a breaking change for the Power BI model and should not be treated as a documentation-only update.