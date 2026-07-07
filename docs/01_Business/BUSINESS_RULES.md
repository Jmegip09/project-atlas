# Business Rules

## Purpose

This document defines the operational rules that govern Project Atlas.

Business rules translate real-world supply chain behavior into constraints, validation logic, data quality checks, and system requirements.

These rules will guide future database design, SQL constraints, Python validation scripts, ETL logic, and Power BI reporting.

---

# Procurement Rules

## ATLAS-RULE-001 — Active Supplier Requirement

New purchase orders may only be created for suppliers with an active status.

### Business Reason

Prevents purchasing from inactive, suspended, or unreliable suppliers.

### Future Implementation

- Supplier status validation
- Purchase order creation checks
- Data quality exception reporting

---

## ATLAS-RULE-002 — Purchase Order Line Requirement

Every purchase order must contain at least one purchase order line.

### Business Reason

A purchase order without items has no operational or financial value.

### Future Implementation

- Purchase order validation
- ETL completeness check
- Data quality rule

---

## ATLAS-RULE-003 — Fully Received Purchase Order

A purchase order may only be marked as fully received when all purchase order line quantities have been received.

### Business Reason

Prevents inaccurate purchase order status reporting.

### Future Implementation

- SQL view calculating received quantities
- PO status validation
- Procurement dashboard logic

---

# Receiving Rules

## ATLAS-RULE-004 — Inventory Increase After Receiving

Inventory should only increase after receiving has been completed and accepted.

### Business Reason

Prevents inventory from becoming available before warehouse verification.

### Future Implementation

- Receiving table
- Inventory transaction records
- Inventory balance update logic

---

## ATLAS-RULE-005 — Damaged or Rejected Inventory

Damaged or rejected inventory should not be added to available stock.

### Business Reason

Prevents unusable inventory from inflating available quantity.

### Future Implementation

- Receiving condition status
- Rejected quantity field
- Data quality checks

---

## ATLAS-RULE-006 — Partial Receiving

Partial receipts must remain tied to the original purchase order line.

### Business Reason

Supports accurate tracking of open quantities and supplier delivery performance.

### Future Implementation

- Receiving records linked to purchase order lines
- Open quantity calculation
- Supplier performance reporting

---

# Inventory Rules

## ATLAS-RULE-007 — Non-Negative Inventory

Inventory quantity on hand cannot be negative.

### Business Reason

Negative inventory indicates a data quality issue, timing issue, or process failure.

### Future Implementation

- Database check constraint
- Python validation rule
- Data quality dashboard alert

---

## ATLAS-RULE-008 — Warehouse/Product Uniqueness

Each warehouse-product combination should have one current inventory balance record.

### Business Reason

Prevents duplicate stock records and inaccurate quantity reporting.

### Future Implementation

- Unique database constraint
- Inventory balance validation
- Duplicate detection rule

---

## ATLAS-RULE-009 — Traceable Inventory Movement

Every inventory movement should generate a transaction record.

### Business Reason

Creates an audit trail for receipts, issues, transfers, adjustments, and cycle count corrections.

### Future Implementation

- Inventory transactions table
- Transaction type field
- Transaction history reporting

---

# Warehouse Transfer Rules

## ATLAS-RULE-010 — Transfer Balance Logic

Warehouse transfers must reduce inventory from the source warehouse and increase inventory at the destination warehouse.

### Business Reason

Ensures inventory remains balanced across locations.

### Future Implementation

- Transfer transaction logic
- Source and destination warehouse validation
- Transfer reconciliation checks

---

## ATLAS-RULE-011 — No Same-Warehouse Transfers

A warehouse transfer cannot have the same source and destination warehouse.

### Business Reason

Prevents meaningless transfer records and reporting noise.

### Future Implementation

- SQL constraint
- ETL validation rule
- Transfer exception report

---

# Cycle Count Rules

## ATLAS-RULE-012 — Cycle Count Variance

Cycle counts compare system quantity against counted quantity.

### Business Reason

Identifies inventory discrepancies and supports inventory accuracy reporting.

### Future Implementation

- Cycle count table
- Variance calculation
- Inventory accuracy KPI

---

## ATLAS-RULE-013 — Adjustment Reason Requirement

Inventory adjustments require an approved reason code.

### Business Reason

Supports auditability and root cause analysis.

### Future Implementation

- Adjustment reason code table
- Required reason field
- Discrepancy dashboard

---

## ATLAS-RULE-014 — Approved Adjustments Update Inventory

Only approved inventory adjustments should update inventory balances.

### Business Reason

Prevents unauthorized changes to inventory records.

### Future Implementation

- Adjustment approval status
- Inventory update procedure
- Audit reporting

---

# Reporting Rules

## ATLAS-RULE-015 — KPI Data Must Be Validated

Dashboards should use validated data sources only.

### Business Reason

Reporting accuracy depends on trusted, reconciled data.

### Future Implementation

- Validated SQL views
- Data quality checks
- Power BI reporting layer

---

## ATLAS-RULE-016 — Data Quality Issues Must Be Logged

Detected data quality issues should be stored for monitoring and review.

### Business Reason

Allows recurring process issues to be identified and corrected.

### Future Implementation

- Data quality issue table
- Python validation logs
- Data quality dashboard

---

# Relationship to Atlas Implementation

These business rules will inform:

- Functional requirements
- Non-functional requirements
- SQL constraints
- Foreign key relationships
- Python validation scripts
- ETL rules
- Power BI dashboard logic
- Data quality monitoring