# Data Quality Rules

## Purpose

This document defines the data quality controls implemented by the Project Atlas Python validation layer and PostgreSQL schema. It also explains how rejected records are identified, quarantined, tested, and prevented from reaching reporting views.

The executable source of truth is:

- `python/validation/validators.py`
- `python/validation/run_validation.py`
- `python/validation/run_receiving_validation.py`
- `sql/schema/02_constraints.sql`
- `sql/migrations/001_receiving_detail_and_inventory_ledger.sql`

---

## Validation Strategy

Project Atlas uses layered controls:

| Layer | Responsibility |
|---|---|
| Python validation | Detect source-data defects before loading and produce an auditable issue log. |
| Clean-row filtering | Exclude flagged records and dependent rows from downstream processing. |
| Business-key resolution | Match supplier, product, warehouse, and purchase order keys to database records. |
| PostgreSQL constraints | Reject invalid values, broken relationships, and duplicate business keys at the system-of-record boundary. |
| Unit tests and CI | Prevent validator behavior from regressing during code changes. |

Validation does not repair source rows automatically. The raw extract remains unchanged, and each issue is written to a processed quality log.

---

## Issue Log Contract

Both quality logs use the same columns:

| Column | Definition |
|---|---|
| `record_id` | Business-key identifier of the rejected record. |
| `rule_id` | Stable identifier for the failed rule or schema control. |
| `field` | Field associated with the failure. |
| `value` | Observed source value. |
| `description` | Human-readable explanation of the failure. |

Record identifier formats:

| Dataset | Format | Example |
|---|---|---|
| PO header | `po_number` | `PO-2026-1004` |
| PO line | `po_number:sku` | `PO-2026-1004:PROD-SKU-1001` |
| Receiving event | `po_number:sku:event_number` | `PO-2026-1004:PROD-SKU-1001:2` |

The current logs do not include a batch ID or validation timestamp. Re-running validation overwrites the previous log.

---

## Purchase Order Header Rules

| Rule ID | Field(s) | Failure Condition | Enforcement |
|---|---|---|---|
| `SCHEMA-uq_po_number` | `po_number` | The same PO number appears more than once in the raw header extract. Both duplicate rows are flagged. | Python and PostgreSQL unique constraint `uq_po_number` |
| `ATLAS-RULE-001` | `supplier_name` | Supplier is blank or null. | Python; database requires a resolved `supplier_id` |
| `ATLAS-RULE-001` | `supplier_name` | Supplier is not present in the validator's known supplier set. | Python plus load-time master-data resolution |
| `SCHEMA-chk_delivery_date` | `order_date`, `expected_delivery_date` | Expected delivery date is before order date. | Python and PostgreSQL check constraint `chk_delivery_date` |
| `SCHEMA-not-null-po_status` | `po_status` | Status is blank or null. | Python |
| `SCHEMA-chk_po_status` | `po_status` | Status is not `Open`, `Partially Received`, `Fully Received`, or `Cancelled`. | Python and PostgreSQL check constraint `chk_po_status` |

---

## Purchase Order Line Rules

| Rule ID | Field(s) | Failure Condition | Enforcement |
|---|---|---|---|
| `SCHEMA-chk_quantity_positive` | `quantity_ordered` | Ordered quantity is negative. | Python; PostgreSQL constraint `chk_qty_ordered` requires greater than zero |
| `SCHEMA-chk_received_vs_ordered` | `quantity_ordered`, `quantity_received` | Received quantity exceeds ordered quantity. | Python and PostgreSQL check constraint `chk_received_vs_ordered` |
| `FK-product_sku` | `sku` | SKU is not present in the validator's known SKU set. | Python plus load-time product resolution |
| `SCHEMA-chk_unit_cost` | `unit_cost` | Unit cost is zero or negative. | Python; PostgreSQL `chk_unit_cost` currently allows zero and rejects only negative values |

Python deliberately applies a stricter cost rule than the database. This is acceptable only if zero-cost purchase order lines are a documented business rejection. Otherwise, the schema and validator must be aligned.

---

## Receiving Event Rules

| Rule ID | Field(s) | Failure Condition | Enforcement |
|---|---|---|---|
| `SCHEMA-chk_receiving_quality_breakdown` | Receipt quantity fields | Accepted + damaged + rejected does not equal gross received. | Python and PostgreSQL check constraint |
| `SCHEMA-chk_receiving_quality_nonnegative` | Receipt quantity fields | Accepted, damaged, or rejected is negative, or gross received is not positive. | Python plus PostgreSQL quality and gross-quantity constraints |
| `LOGIC-received_before_ordered` | `order_date`, `received_date` | Receipt timestamp occurs before the PO order date. | Python |
| `FK-warehouse_code` | `warehouse_code` | Warehouse code is not recognized. | Python plus load-time warehouse resolution |
| `SCHEMA-uq_receiving_po_line_event` | `po_number`, `sku`, `event_number` | The same event number appears more than once for a PO line. Both duplicate rows are flagged. | Python and PostgreSQL unique constraint on `(po_line_id, event_number)` |

---

## Quarantine Behavior

### Purchase Orders

`etl.clean_rows.get_clean_po_lines` reads `data_quality_log.csv` and applies these rules:

- A PO header with any issue is excluded from loading.
- All lines belonging to an excluded header are also excluded.
- A line with its own issue is excluded.
- Other clean lines for the same clean header remain eligible.

The same clean-row function feeds both `etl.load` and `etl.generate_receiving_raw`, preventing receiving data from being generated for a rejected purchase order.

### Receiving Events

`etl.load_receiving` builds the receiving record identifier and excludes every identifier present in `receiving_quality_log.csv`. Clean rows are then resolved to `po_line_id` and `warehouse_id` before insert.

If duplicate raw events share the same identifier, the validator flags both; therefore both are excluded.

---

## Database Integrity Controls

Key schema controls include:

- Unique PO numbers
- One inventory balance per warehouse-product pair
- One receiving event number per purchase order line
- Valid supplier, product, warehouse, employee, and department foreign keys
- Non-negative inventory balances and safety stock
- Positive ordered and received quantities
- Received PO quantity not exceeding ordered quantity
- Expected delivery not preceding order date
- Valid supplier, PO, employee, department, and ledger transaction statuses/types
- Receiving quantity reconciliation and non-negative outcome quantities
- One opening-balance ledger entry per warehouse-product pair

Python validation improves issue reporting, but PostgreSQL remains the final authority. A loader must not bypass constraints to force rejected data into the database.

---

## Tests and Coverage

The repository contains 17 validator unit tests:

- Nine tests for PO header and line validation behavior
- Eight tests for receiving validation behavior

Tests run in GitHub Actions on pushes and pull requests to `main`.

Current tests verify positive and negative examples for most validator functions. The following controls are implemented but do not have direct unit tests:

- Blank PO status
- Invalid PO status
- Combined `run_all` output schema
- Combined `run_receiving_validation` output schema
- Parent-header quarantine behavior in `clean_rows`
- Loader behavior when a business key cannot be resolved
- Database constraint enforcement

---

## Known Gaps and Required Hardening

The current validation layer has several boundaries that should be treated as open work, not hidden assumptions:

1. **Static master-data sets.** Valid suppliers, SKUs, and warehouse codes are duplicated in Python. They can drift from PostgreSQL seed data. A future validator should load reference data from a controlled source or shared configuration.
2. **Zero ordered quantity mismatch.** Python flags only negative `quantity_ordered`, while PostgreSQL requires a value greater than zero. A zero value can pass Python and fail during load.
3. **Unit-cost mismatch.** Python rejects zero cost while PostgreSQL permits it. The business rule needs one consistent answer.
4. **Malformed or missing dates.** Date parsing uses `errors="coerce"`; invalid values can become `NaT` and avoid a less-than comparison. Explicit required-date and valid-date rules are needed.
5. **Malformed numeric values.** Numeric coercion can create `NaN`; current comparisons do not consistently flag every `NaN` case.
6. **No source schema contract.** Missing, renamed, or extra CSV columns are not validated before field access.
7. **No batch history.** Quality logs are overwritten and have no run ID, timestamp, source filename checksum, or row-count reconciliation.
8. **No severity or disposition.** Every issue is treated as a rejection; warnings and informational controls are not modeled.
9. **No integration tests.** Constraint names, loader transactions, ledger reconciliation, and rerun behavior are not exercised against PostgreSQL in CI.

These gaps do not invalidate the current portfolio pipeline, but they define the difference between a demonstrable batch-quality framework and a production-ready control system.

---

## Rule Change Control

Any new or modified data quality rule must include:

- A stable `rule_id` aligned with the business rule or schema constraint.
- At least one failing and one passing test case.
- A documented record-level disposition.
- Review of dependent loaders and dashboard metrics.
- Alignment between Python behavior and PostgreSQL constraints.
- An entry in the changelog when behavior changes.