# Data Classification Strategy

## Purpose

Project Atlas organizes its data into three primary categories based on how the information is created, maintained, and consumed throughout the system.

Separating data into logical groups improves database organization, simplifies ETL development, supports reporting, and mirrors the architecture commonly found in enterprise ERP and analytics platforms.

---

# Master Data

Master data represents the core business entities that change infrequently and provide the foundation for daily operations.

These records are typically created once and updated only when business information changes.

### Current Master Data

- Suppliers
- Products
- Warehouses
- Departments
- Employees

### Characteristics

- Low frequency of change
- Referenced by transactional data
- Supports referential integrity
- Forms the foundation of the operational database

---

# Transaction Data

Transaction data captures the day-to-day operational activities performed by the organization.

These records are continuously generated as business events occur and represent the operational history of Atlas Distribution Company.

### Current Transaction Data

- Purchase Orders
- Purchase Order Lines
- Receiving
- Inventory Transactions
- Warehouse Transfers
- Cycle Counts
- Inventory Adjustments

### Characteristics

- High transaction volume
- Continuously growing
- Records historical business events
- Supports operational reporting and auditing

---

# Analytical Data

Analytical data is derived from operational data and optimized for business intelligence, reporting, and decision-making.

Rather than storing raw business events, this layer transforms operational information into meaningful metrics and insights.

### Current Analytical Objects

- SQL Views
- KPIs
- Power BI Dashboards

### Future Analytical Objects

- Materialized Views
- Fact Tables
- Dimension Tables
- dbt Models
- Snowflake Data Warehouse
- Executive Scorecards

### Characteristics

- Read-optimized
- Supports business intelligence
- Aggregates operational data
- Designed for executive and analytical reporting

---

# Relationship to Project Atlas

This data classification strategy influences the design of:

- Database Schema
- Entity Relationship Diagram (ERD)
- ETL Pipelines
- SQL Views
- Data Quality Framework
- Power BI Dashboards
- Future Data Warehouse Architecture