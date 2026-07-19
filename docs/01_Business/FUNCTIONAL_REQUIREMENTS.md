# Functional Requirements

## Purpose

This document defines the behavior Project Atlas must provide to support procurement, receiving, inventory control, data quality, and business intelligence. Each requirement is written as a verifiable system capability and is mapped to implementation evidence in the repository.

Business needs are defined in `BUSINESS_REQUIREMENTS.md`; operational policies are defined in `BUSINESS_RULES.md`. This document translates those needs and rules into technical behavior.

---

## Status Definitions

| Status | Meaning |
|---|---|
| Implemented | The requirement is present in the current repository and has direct implementation evidence. |
| Partially Implemented | A usable portion exists, but one or more acceptance criteria remain incomplete. |
| Planned | The required data model or workflow has not been implemented. |

---

## Scope Boundary

The current platform is a deterministic batch analytics system. Data becomes current after the Python pipeline loads PostgreSQL and Power BI refreshes its reporting views. The platform does not provide streaming ingestion, event-driven updates, or real-time dashboard refresh.

Therefore, the "real-time visibility" objective in `ATLAS-BR-001` is implemented in the current release as refreshed current-state visibility, not literal real-time processing.

---

## Requirements Summary

| ID | Capability | Priority | Status |
|---|---|---|---|
| `ATLAS-FR-001` | Supplier master-data control | High | Partially Implemented |
| `ATLAS-FR-002` | Product and warehouse reference data | High | Partially Implemented |
| `ATLAS-FR-003` | Purchase order ingestion | High | Implemented |
| `ATLAS-FR-004` | Purchase order validation and quarantine | High | Implemented |
| `ATLAS-FR-005` | Business-key resolution and clean PO loading | High | Implemented |
| `ATLAS-FR-006` | Receiving-event simulation | High | Implemented |
| `ATLAS-FR-007` | Receiving validation and quarantine | High | Implemented |
| `ATLAS-FR-008` | Partial receipt and inspection tracking | High | Implemented |
| `ATLAS-FR-009` | Inventory transaction ledger and balances | High | Partially Implemented |
| `ATLAS-FR-010` | Multi-warehouse inventory-risk reporting | High | Partially Implemented |
| `ATLAS-FR-011` | Supplier scorecard reporting | High | Partially Implemented |
| `ATLAS-FR-012` | Receiving and quality reporting | High | Partially Implemented |
| `ATLAS-FR-013` | Operational analytical queries | Medium | Implemented |
| `ATLAS-FR-014` | Automated validation testing | High | Partially Implemented |
| `ATLAS-FR-015` | Power BI refresh and presentation | High | Partially Implemented |

---

## ATLAS-FR-001 — Supplier Master-Data Control

### Requirement

The system shall maintain uniquely identifiable suppliers with business names, contact information, quoted lead time, and controlled status values.

### Acceptance Criteria

- Supplier records receive a surrogate `supplier_id`.
- Supplier status is limited to `Active`, `On Hold`, or `Inactive`.
- Quoted lead time cannot be negative.
- Purchase order source records must resolve to a known supplier before loading.
- New purchase orders must not be created for a supplier that is not active.

### Implementation Evidence

- `suppliers` table in `sql/schema/01_database_setup.sql`
- Supplier constraints in `sql/schema/02_constraints.sql`
- Supplier seed data in `sql/seed/01_suppliers.sql`
- Supplier validation and lookup logic in `python/validation/validators.py` and `python/etl/load.py`

### Current Gap

Known-supplier validation is implemented, but the loader does not check `supplier_status = 'Active'` before inserting a purchase order. `ATLAS-RULE-001` is therefore only partially enforced.

---

## ATLAS-FR-002 — Product and Warehouse Reference Data

### Requirement

The system shall maintain products and warehouses using stable business keys that can be resolved to database surrogate identifiers during ETL.

### Acceptance Criteria

- Products have unique business SKUs and non-negative safety-stock levels.
- Warehouses have business codes, names, and locations.
- ETL source records use `sku` and `warehouse_code` rather than internal database IDs.
- Receiving and inventory records must reference valid products and warehouses.

### Implementation Evidence

- `products` and `warehouses` tables
- Product and warehouse seed scripts
- Foreign-key constraints in `sql/schema/02_constraints.sql`
- Business-key resolution in the purchase order and receiving loaders

### Status Note

The current schema indexes `products.sku` but does not enforce a unique constraint on `sku` or `warehouses.warehouse_code`. Lookup behavior assumes uniqueness, so database uniqueness should be added before production use.

---

## ATLAS-FR-003 — Purchase Order Ingestion

### Requirement

The system shall ingest purchase order headers and lines from source-style extracts that use business keys rather than database surrogate IDs.

### Acceptance Criteria

- Header data includes PO number, supplier, order date, expected delivery date, and status.
- Line data includes PO number, SKU, ordered quantity, received quantity, and unit cost.
- One purchase order can contain multiple product lines.
- The source generator produces reproducible data for development and testing.
- Source files remain unchanged during validation.

### Implementation Evidence

- `python/etl/generate_data.py`
- `python/data/raw/purchase_orders_raw.csv`
- `python/data/raw/purchase_order_lines_raw.csv`

---

## ATLAS-FR-004 — Purchase Order Validation and Quarantine

### Requirement

The system shall validate raw purchase order data, log every detected issue, and prevent flagged records from entering PostgreSQL.

### Acceptance Criteria

- Duplicate PO numbers are detected.
- Missing and unknown suppliers are detected.
- Invalid date order and PO status are detected.
- Invalid quantities, over-receipts, unknown SKUs, and non-positive cost are detected.
- Each issue identifies the record, rule, field, observed value, and description.
- A rejected header also excludes its dependent line records.
- Clean source rows remain eligible for loading.

### Implementation Evidence

- `python/validation/validators.py`
- `python/validation/run_validation.py`
- `python/etl/clean_rows.py`
- `python/data/processed/data_quality_log.csv`
- `docs/05_ETL/DATA_QUALITY_RULES.md`

---

## ATLAS-FR-005 — Business-Key Resolution and Clean PO Loading

### Requirement

The system shall load only clean purchase order records and resolve source business keys to PostgreSQL surrogate keys.

### Acceptance Criteria

- `supplier_name` resolves to `supplier_id`.
- `sku` resolves to `product_id`.
- Inserted headers return `po_id` for their dependent lines.
- Unresolved keys are excluded rather than inserted as invalid foreign keys.
- Re-running the loader does not duplicate an existing PO number.
- Header and line inserts execute within a database transaction.

### Implementation Evidence

- `python/etl/load.py`
- Unique PO-number and foreign-key constraints
- Shared filtering in `python/etl/clean_rows.py`

---

## ATLAS-FR-006 — Receiving-Event Simulation

### Requirement

The system shall generate realistic receiving events from clean purchase order lines with received quantities.

### Acceptance Criteria

- Receiving events derive from clean PO rows rather than being generated independently.
- Supplier profiles influence timeliness, partial receipts, damage, and rejection.
- Warehouse profiles influence inspection-delay timing.
- A PO line may produce one or two receiving events.
- Event quantities reconcile gross, accepted, damaged, and rejected units.
- Source events use PO number, SKU, and warehouse code as business keys.

### Implementation Evidence

- `python/config/profiles.py`
- `python/etl/generate_receiving_raw.py`
- `python/data/raw/receiving_events_raw.csv`

---

## ATLAS-FR-007 — Receiving Validation and Quarantine

### Requirement

The system shall detect invalid receiving events and prevent them from updating receiving history or inventory.

### Acceptance Criteria

- Gross quantity must equal accepted plus damaged plus rejected quantities.
- Receiving quantities must be valid and non-negative.
- Receipt date cannot precede PO order date.
- Warehouse code must be recognized.
- Duplicate event numbers for the same PO line are rejected.
- Every issue is written to the receiving quality log.

### Implementation Evidence

- Receiving validators in `python/validation/validators.py`
- `python/validation/run_receiving_validation.py`
- `python/data/processed/receiving_quality_log.csv`

---

## ATLAS-FR-008 — Partial Receipt and Inspection Tracking

### Requirement

The system shall preserve multiple receipt events for a purchase order line and separately record accepted, damaged, and rejected quantities.

### Acceptance Criteria

- Every event remains linked to its original `po_line_id`.
- `(po_line_id, event_number)` is unique.
- Gross quantity reconciles to the three inspection outcomes.
- Damaged and rejected quantities never increase sellable inventory.
- Event date, warehouse, and inspection results remain queryable.

### Implementation Evidence

- `receiving_transactions`
- `sql/migrations/001_receiving_detail_and_inventory_ledger.sql`
- `python/etl/load_receiving.py`

---

## ATLAS-FR-009 — Inventory Transaction Ledger and Balances

### Requirement

The system shall record inventory movement in an append-only ledger and derive current warehouse-product balances from ledger quantities.

### Acceptance Criteria

- Initial quantities create one `OPENING_BALANCE` transaction per warehouse-product pair.
- Accepted receiving quantities create `RECEIPT` transactions.
- A receipt ledger row references its receiving event.
- Re-running the receiving load does not duplicate ledger movements.
- Current balance equals the sum of transaction deltas by warehouse and product.
- Inventory quantity on hand cannot be negative.

### Implementation Evidence

- `inventory_transactions` migration
- `inventory_balances`
- `seed_opening_balances` and `recompute_balances` in `python/etl/load_receiving.py`

### Current Gap

The ledger permits `ADJUSTMENT` and `SHIPMENT` transaction types, but the current pipeline creates only `OPENING_BALANCE` and `RECEIPT` records. Consumption, transfers, cycle counts, and approved adjustments remain planned capabilities.

---

## ATLAS-FR-010 — Multi-Warehouse Inventory-Risk Reporting

### Requirement

The system shall provide a current inventory and safety-stock position for every populated warehouse-product balance.

### Acceptance Criteria

- Each row identifies warehouse, product, quantity on hand, and safety stock.
- Units above safety stock are calculated consistently.
- A warehouse-product row is flagged at risk when quantity on hand is equal to or below safety stock.
- Users can identify the deepest shortages first.
- Dashboard totals reconcile to the reporting view after refresh.

### Implementation Evidence

- `sql/views/vw_inventory_status.sql`
- `sql/queries/01_stockout_risk.sql`
- Inventory Risk page in `powerbi/ProjectAtlas.pbix`

### Status Note

The reporting view is complete. The Power BI table still requires the documented shortfall sort, and the warehouse chart must be changed from quantity on hand to a count of at-risk locations.

---

## ATLAS-FR-011 — Supplier Scorecard Reporting

### Requirement

The system shall compare suppliers using quoted lead time, planned lead-time variance, purchase order count, and purchase order value.

### Acceptance Criteria

- Every supplier appears once in the reporting view.
- Suppliers with no purchase orders remain visible.
- Planned lead time and variance are defined consistently.
- Supplier comparisons are sorted from worst to best variance.
- Dashboard labels do not imply actual on-time delivery when using planned dates.

### Implementation Evidence

- `sql/views/vw_supplier_performance.sql`
- `sql/queries/02_supplier_delivery_performance.sql`
- Supplier Scorecard page in Power BI

### Current Gap

The view and primary comparison visuals exist, but the Total Suppliers and Average Supplier Lead-Time Variance cards remain incomplete. Actual supplier on-time delivery requires a receipt-based metric at an agreed grain.

---

## ATLAS-FR-012 — Receiving and Quality Reporting

### Requirement

The system shall expose receipt volume, timing variance, and inspection outcomes for analysis by supplier and warehouse.

### Acceptance Criteria

- Every reporting row represents one receiving event.
- Users can distinguish early, on-time, and late events through `days_late`.
- Accepted, damaged, and rejected quantities reconcile to gross received quantity.
- Users can compare receipt quality by supplier.
- Users can count late receiving events by warehouse.

### Implementation Evidence

- `sql/views/vw_receiving_performance.sql`
- `sql/queries/04_receiving_bottlenecks.sql`
- Receiving & Quality page in Power BI

### Current Gap

The existing warehouse chart counts all receiving events. It must apply `days_late > 0` before it satisfies the late-event requirement.

---

## ATLAS-FR-013 — Operational Analytical Queries

### Requirement

The system shall provide reusable SQL analyses for the project's documented business questions.

### Acceptance Criteria

The SQL layer can identify:

- Warehouse-product positions at stockout risk
- Supplier planned lead-time variance
- Open and partially received purchase orders with outstanding value
- Receiving timing by warehouse
- Quantity shortfalls and damaged/rejected concentration

### Implementation Evidence

- `sql/queries/01_stockout_risk.sql`
- `sql/queries/02_supplier_delivery_performance.sql`
- `sql/queries/03_open_purchase_orders.sql`
- `sql/queries/04_receiving_bottlenecks.sql`
- `sql/queries/05_inventory_discrepancies.sql`

---

## ATLAS-FR-014 — Automated Validation Testing

### Requirement

The system shall automatically test data-validation behavior on changes to the main branch and on pull requests.

### Acceptance Criteria

- Validator tests can run locally from the `python/` directory.
- CI uses the supported Python version and installs declared dependencies.
- A failing assertion causes the workflow to fail.
- Every new validation rule includes passing and failing test cases.

### Implementation Evidence

- `python/tests/test_validators.py`
- `python/pytest.ini`
- `.github/workflows/test.yml`

### Status Note

The current suite contains 17 unit tests. Database integration and end-to-end pipeline tests are not yet implemented.

---

## ATLAS-FR-015 — Power BI Refresh and Presentation

### Requirement

The system shall present validated supplier, inventory, and receiving information through a three-page Power BI report.

### Acceptance Criteria

- Power BI connects to the three `vw_` reporting views.
- Each page uses the view assigned in `DASHBOARD_REQUIREMENTS.md`.
- Cards use explicit, correctly labeled measures.
- Detail tables allow investigation of summary results.
- Dashboard results reconcile to PostgreSQL after refresh.
- No unsupported future metric is presented as implemented.

### Implementation Evidence

- `powerbi/ProjectAtlas.pbix`
- `docs/06_POWER_BI/DASHBOARD_REQUIREMENTS.md`
- `docs/06_POWER_BI/KPI_CATALOG.md`

### Current Gap

The three-page report exists, but the version 0.6 acceptance gaps documented in `DASHBOARD_REQUIREMENTS.md` must be resolved before this requirement is complete.

---

## Deferred Functional Scope

The following capabilities are intentionally planned rather than implied by the current implementation:

- Supplier shipment and in-transit tracking
- Demand consumption and outbound shipments
- Warehouse transfer workflow
- Cycle counting and variance approval
- Inventory adjustment reasons and approvals
- Demand forecasting and reorder recommendations
- User authentication and role-based application access
- Scheduled orchestration and automated Power BI refresh

These capabilities require new business events, tables, validation rules, and reporting contracts before they can be treated as functional requirements of a released version.

---

## Traceability Matrix

| Requirement Group | Business Rules | Primary Implementation |
|---|---|---|
| Supplier and PO control | `ATLAS-RULE-001`–`003` | Supplier/PO schema, PO validators, `etl.load` |
| Receiving and inspection | `ATLAS-RULE-004`–`006` | Receiving generator, validators, transactions |
| Inventory integrity | `ATLAS-RULE-007`–`009` | Inventory ledger, balance recomputation, inventory view |
| Transfers and counts | `ATLAS-RULE-010`–`014` | Planned |
| Reporting and quality | `ATLAS-RULE-015`–`016` | Quality logs, reporting views, Power BI |

Requirement status must be updated when implementation changes. A requirement is not complete merely because a table or visual exists; every acceptance criterion must be satisfied.