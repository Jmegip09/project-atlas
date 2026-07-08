# Seed Data

## Purpose

This document defines the strategy for generating realistic sample data used throughout Project Atlas.

Rather than relying on randomly generated records, the seed data will simulate day-to-day operations of a fictional supply chain organization. The goal is to create business scenarios that support SQL development, ETL pipelines, reporting, data quality validation, and business intelligence.

Seed data serves as the operational foundation for testing the database, validating business rules, and demonstrating analytical capabilities.

---

# Objectives

The seed data should:

- Simulate realistic business operations
- Maintain referential integrity
- Support analytical SQL queries
- Provide meaningful reporting scenarios
- Enable ETL development and testing
- Demonstrate common supply chain challenges

---

# Planned Seed Data

## Master Data

- Suppliers
- Products
- Warehouses
- Employees (Future)

---

## Procurement

- Purchase Orders
- Purchase Order Lines

---

## Inventory

- Inventory Balances
- Inventory Transactions (Future)

---

## Warehouse Operations

- Receiving Records (Future)
- Warehouse Transfers (Future)
- Cycle Counts (Future)
- Inventory Adjustments (Future)

---

# Business Scenarios

The seed data will include scenarios such as:

- Late supplier deliveries
- Partial purchase order receipts
- Inventory shortages
- Overstock situations
- Warehouse transfers
- Cycle count discrepancies
- Inventory adjustments
- Supplier performance differences

These scenarios will support realistic business analysis and reporting.

---

# Data Volume Targets

Initial Version:

| Entity | Target Records |
|----------|---------------:|
| Suppliers | 20 |
| Products | 500 |
| Warehouses | 5 |
| Purchase Orders | 1,000 |
| Purchase Order Lines | 5,000+ |
| Inventory Balances | 2,500+ |

Future versions will significantly increase data volume to better simulate enterprise-scale environments.

---

# Relationship to Project Atlas

The seed data supports:

- Database Testing
- Business Rules Validation
- SQL Query Development
- ETL Pipelines
- Data Quality Framework
- Power BI Dashboards
- Performance Testing
- End-to-End Business Process Simulation