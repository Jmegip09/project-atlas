
# Entity Relationship Diagram (ERD)

## Purpose

This document defines the logical data model for Project Atlas.

The Entity Relationship Diagram (ERD) illustrates how business entities interact within the supply chain intelligence platform. It serves as the blueprint for the PostgreSQL database by documenting table relationships, primary keys, foreign keys, and data dependencies before implementation.

The ERD ensures that the database accurately represents the business processes documented throughout Project Atlas while supporting analytics, reporting, and future system expansion.

---

# Design Objectives

The ERD has been designed to:

- Normalize operational data
- Minimize redundancy
- Maintain referential integrity
- Support scalable reporting
- Enable efficient SQL querying
- Provide a clear separation between master data and transactional data
- Serve as the foundation for future ETL pipelines and Power BI dashboards

---

# Core Entity Groups

The Project Atlas database is organized into the following logical groups:

## Master Data

Reference information that changes infrequently.

- Suppliers
- Products
- Warehouses
- Employees

---

## Procurement

Tracks purchasing activities.

- Purchase Orders
- Purchase Order Lines

---

## Inventory Management

Tracks current inventory status and movements.

- Inventory Balances
- Inventory Transactions

---

## Warehouse Operations

Supports inventory movement and physical operations.

- Receiving
- Warehouse Transfers
- Cycle Counts
- Inventory Adjustments

---

## Analytics

Provides reporting and business intelligence.

- SQL Views
- Materialized Views (Future)
- Power BI Semantic Model (Future)

---

# High-Level Entity Relationships

```text
Suppliers
    │
    │ 1
    │
    └──────────────< Purchase Orders
                          │
                          │ 1
                          │
                          └──────────────< Purchase Order Lines
                                                 │
                                                 │
                                                 ▼
                                             Products
                                                 │
                                                 │
                                                 ▼
                                         Inventory Balances
                                                 │
                                                 │
                                                 ▼
                                     Inventory Transactions
                                                 │
                                                 ▼
                                            Warehouses
```

---

# Relationship Summary

| Parent Entity | Child Entity | Relationship |
|---------------|--------------|--------------|
| Suppliers | Purchase Orders | One-to-Many |
| Purchase Orders | Purchase Order Lines | One-to-Many |
| Products | Purchase Order Lines | One-to-Many |
| Products | Inventory Balances | One-to-Many |
| Warehouses | Inventory Balances | One-to-Many |
| Inventory Balances | Inventory Transactions | One-to-Many |
| Warehouses | Inventory Transactions | One-to-Many |

---

# Primary Keys

Each entity contains a surrogate primary key generated using PostgreSQL identity columns.

Examples:

- supplier_id
- product_id
- warehouse_id
- po_id
- po_line_id
- inventory_id
- transaction_id

---

# Foreign Keys

Relationships between entities are enforced through foreign key constraints to ensure referential integrity.

Examples include:

- purchase_orders.supplier_id
- purchase_order_lines.po_id
- purchase_order_lines.product_id
- inventory_balances.product_id
- inventory_balances.warehouse_id
- inventory_transactions.inventory_id

---

# Normalization Strategy

Project Atlas follows Third Normal Form (3NF) during Version 1 development.

Objectives include:

- Eliminate duplicate data
- Separate master and transactional data
- Reduce update anomalies
- Improve maintainability
- Support scalable reporting

Future versions may introduce dimensional modeling for analytics while preserving the normalized operational database.

---

# Future Expansion

The ERD is designed to support additional entities without major redesign.

Planned future additions include:

- Shipments
- Vendors
- Locations
- Reorder Recommendations
- Forecasting
- Purchase Requisitions
- Work Orders
- Audit Logs
- Data Quality Exceptions

---

# Relationship to Project Atlas

The Entity Relationship Diagram supports:

- Business Requirements
- Business Process Flow
- Business Rules
- Database Schema
- Data Dictionary
- SQL Development
- ETL Pipelines
- Power BI Dashboards
- Future Data Warehouse Design
```