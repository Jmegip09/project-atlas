# Architecture Decision Records (ADRs)

## Purpose

This document records the significant architectural and technical decisions made throughout the development of Project Atlas.

Rather than documenting implementation details, these records explain why specific approaches were chosen, what alternatives were considered, and how each decision supports the long-term goals of the project.

Maintaining Architecture Decision Records (ADRs) improves project maintainability, provides historical context, and demonstrates professional software engineering practices.

---

# ADR-001 — Documentation-First Development

## Status

Accepted

## Date

July 2026

## Decision

Business documentation will be completed before major implementation work begins.

## Context

Project Atlas is intended to simulate an enterprise software project. Business requirements, architecture, and database design should drive implementation rather than evolve after code is written.

## Alternatives Considered

- Build the database first
- Build dashboards first
- Develop documentation alongside implementation

## Consequences

### Positive

- Clear project direction
- Better traceability
- Easier future expansion
- Stronger portfolio presentation

### Negative

- Longer planning phase
- Slower initial development

---

# ADR-002 — Modular Database Structure

## Status

Accepted

## Date

July 2026

## Decision

Database objects are separated into multiple SQL scripts rather than maintained in a single monolithic file.

## Context

As Project Atlas grows, separating schema objects into focused scripts improves readability, maintainability, version control, and deployment flexibility.

## Alternatives Considered

- Single SQL deployment script
- Split scripts by database object type

## Consequences

### Positive

- Easier maintenance
- Cleaner Git history
- Modular deployments
- Enterprise-style organization

### Implemented Files

- `01_database_setup.sql`
- `02_constraints.sql`
- `03_indexes.sql`
- `04_seed_data.sql`
- Future views, procedures, functions, and migrations

---

# ADR-003 — Separate Inventory Balances from Inventory Transactions

## Status

Accepted

## Date

July 2026

## Decision

Current inventory balances will be stored separately from inventory transaction history.

## Context

Inventory balances represent the current state of inventory, while inventory transactions record every movement affecting inventory over time.

Separating these concepts simplifies reporting while preserving historical traceability.

## Alternatives Considered

- Calculate balances from transaction history
- Maintain dedicated balance records

## Consequences

### Positive

- Faster inventory reporting
- Simpler SQL queries
- Better scalability
- Common ERP design pattern

---

# ADR-004 — Enterprise Repository Organization

## Status

Accepted

## Date

July 2026

## Decision

The repository is organized by functional responsibility rather than programming language or implementation phase.

## Context

Project Atlas is intended to resemble the structure of enterprise analytics and software engineering repositories.

## Repository Structure

```text
docs/
sql/
python/
powerbi/
data/
diagrams/
```

## Consequences

### Positive

- Improved navigation
- Separation of concerns
- Easier onboarding
- Supports long-term growth

---

# ADR-005 — Fictional Supply Chain Company

## Status

Accepted

## Date

July 2026

## Decision

Project Atlas models a fictional supply chain organization rather than replicating any real employer or proprietary business processes.

## Context

The project is inspired by general supply chain operations while remaining independent of confidential systems or organizational data.

## Consequences

### Positive

- Ethical portfolio development
- No proprietary information
- Unlimited design flexibility
- Realistic business scenarios

---

# ADR-006 — PostgreSQL as the Operational Database

## Status

Accepted

## Date

July 2026

## Decision

PostgreSQL will serve as the operational database for Project Atlas.

## Context

PostgreSQL provides a robust relational database platform capable of supporting transactional processing, analytical SQL, and future cloud deployment.

## Future Expansion

Future versions may integrate:

- AWS RDS
- Snowflake
- dbt
- Data warehouse architecture

while maintaining PostgreSQL as the operational data source.

---

# ADR-007 — Business Processes Drive Technical Design

## Status

Accepted

## Date

July 2026

## Decision

Business processes will be modeled before designing database objects, ETL pipelines, dashboards, or analytical queries.

## Context

Project Atlas prioritizes solving business problems rather than showcasing isolated technical skills.

Every table, SQL query, Python script, ETL process, and dashboard should trace directly back to a documented business requirement or operational process.

## Consequences

### Positive

- Strong alignment between business and technical implementation
- Improved traceability
- Better architectural consistency
- Easier future expansion
- More realistic enterprise development workflow

---

# Relationship to Project Atlas

The Architecture Decision Records support:

- Business Requirements
- Business Process Flow
- Business Rules
- System Architecture
- Entity Relationship Diagram (ERD)
- Database Design
- SQL Development
- ETL Pipelines
- Power BI Dashboards
- Future Cloud Architecture
- Long-term Project Governance