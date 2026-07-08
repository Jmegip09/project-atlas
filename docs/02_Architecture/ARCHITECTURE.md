# System Architecture

## Purpose

This document defines the high-level architecture of Project Atlas.

Rather than focusing on implementation details, this document describes how the major components of the platform interact to support inventory management, procurement, warehouse operations, data engineering, business intelligence, and executive decision-making.

The architecture establishes the foundation that guides database design, ETL development, reporting, cloud deployment, and future platform expansion.

---

# Architecture Overview

Project Atlas is designed as a modular supply chain intelligence platform inspired by modern enterprise data systems.

The platform separates business operations, data storage, transformation pipelines, analytics, and reporting into independent layers. This separation improves maintainability, scalability, and traceability while allowing each component to evolve independently as the project grows.

Rather than serving as a simple inventory application, Atlas models how operational data flows through an organization—from procurement and warehouse activities to executive dashboards that support strategic decision-making.

---

# System Goals

The architecture is designed to achieve the following objectives:

- Modular and maintainable system design
- Enterprise-inspired software architecture
- Strong data quality and integrity
- Clear separation of responsibilities between system components
- Scalable data model capable of future expansion
- Support for analytics-driven decision making
- End-to-end traceability of inventory transactions
- Documentation-first development approach

---

# System Components

Project Atlas consists of five primary architectural layers:

```text
Business Operations
        ↓
PostgreSQL Database
        ↓
Python ETL Pipeline
        ↓
Analytics SQL Layer
        ↓
Power BI Dashboards
        ↓
Business Decision Making
```

Each layer has a specific responsibility and communicates only with the adjacent layers.

---

# Data Flow

Operational data moves through Atlas using the following lifecycle:

```text
Supplier
        ↓
Purchase Order
        ↓
Receiving & Inspection
        ↓
Inventory Storage
        ↓
Inventory Transactions
        ↓
Data Validation
        ↓
Analytics SQL
        ↓
Power BI Dashboards
        ↓
Executive Decision Making
```

Every business event generates operational data that is validated, stored, transformed, and ultimately presented as business intelligence.

---

# Technology Stack

| Layer | Technology |
|--------|------------|
| Database | PostgreSQL |
| SQL | PostgreSQL SQL |
| Programming | Python |
| Data Processing | Pandas |
| Version Control | Git & GitHub |
| Visualization | Power BI |
| Cloud (Future) | AWS RDS |
| Data Warehouse (Future) | Snowflake |
| Analytics Engineering (Future) | dbt |

---

# Database Layer

The PostgreSQL database serves as the system of record for Project Atlas.

This layer stores both master and transactional data while enforcing referential integrity and business constraints.

Responsibilities include:

- Master data management
- Transaction storage
- Referential integrity
- Data validation
- Inventory state management
- Performance optimization through indexing

---

# ETL Layer

The ETL layer is responsible for preparing data for analytics.

Incoming data will be validated, cleaned, transformed, and loaded into PostgreSQL before becoming available for reporting.

Planned workflow:

```text
Raw Data
        ↓
Validation
        ↓
Cleaning
        ↓
Transformation
        ↓
PostgreSQL
        ↓
Quality Verification
```

Future implementations will include logging, exception handling, and automated pipeline execution.

---

# Analytics Layer

The analytics layer transforms operational data into business information.

Rather than querying transactional tables directly, analytical SQL views will provide curated datasets optimized for reporting.

Examples include:

- Inventory valuation
- Supplier performance
- Purchase order status
- Receiving performance
- Warehouse utilization
- Inventory turnover
- Stockout risk
- Inventory reconciliation

---

# Reporting Layer

Power BI serves as the presentation layer for Project Atlas.

Dashboards will consume validated analytical views instead of raw database tables to ensure consistency, performance, and maintainability.

Planned dashboards include:

- Executive Dashboard
- Inventory Dashboard
- Warehouse Operations Dashboard
- Procurement Dashboard
- Supplier Performance Dashboard
- Data Quality Dashboard

---

# Repository Organization

The repository is organized into functional areas that mirror enterprise software development practices.

```text
docs/
Project documentation

sql/
Database objects

python/
ETL and automation

powerbi/
Business intelligence assets

data/
Sample datasets

diagrams/
Architecture and database diagrams
```

This structure promotes separation of concerns and supports long-term maintainability.

---

# Future Architecture

Project Atlas is designed to evolve over time as new technologies and capabilities are introduced.

Planned enhancements include:

- AWS RDS deployment
- Snowflake data warehouse
- dbt transformation layer
- Automated ETL scheduling
- GitHub Actions
- Docker containerization
- CI/CD pipelines
- Automated testing
- Advanced data quality monitoring

---

# Architecture Decisions

The following architectural decisions guide Project Atlas.

### ADR-001 — Modular SQL Structure

Database objects are separated into individual scripts for tables, constraints, indexes, views, functions, and procedures to improve maintainability.

---

### ADR-002 — Documentation-First Development

Business requirements and architectural decisions are documented before implementation to ensure technical work aligns with business objectives.

---

### ADR-003 — Layered Reporting Architecture

Power BI dashboards consume analytical SQL views rather than transactional tables to improve performance and maintain a consistent reporting layer.

---

### ADR-004 — Enterprise-Inspired Repository Structure

The repository is organized to reflect how enterprise analytics and software engineering projects are commonly structured, separating documentation, database objects, ETL code, reporting assets, and supporting resources.

---

### ADR-005 — Realistic Business Simulation

Project Atlas uses fictional data and independently designed business processes inspired by general supply chain operations. No proprietary employer data or confidential business logic is used.

---

# Relationship to Project Atlas

This architecture serves as the foundation for:

- Entity Relationship Diagram (ERD)
- Data Dictionary
- PostgreSQL Database Schema
- ETL Pipeline Design
- SQL Views and Analytics
- Power BI Dashboards
- Cloud Deployment Strategy
- Future Analytics Engineering Enhancements
