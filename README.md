# Project Atlas

## Enterprise Supply Chain Intelligence Platform

Project Atlas is an enterprise-style supply chain intelligence platform that evolves my CS-499 Inventory Management System capstone into a modern data engineering, analytics, and business intelligence project.

Rather than treating my university capstone as a finished academic assignment, I chose to continue developing it using technologies, certifications, and real-world operational experience to simulate how enterprise organizations manage inventory, procurement, warehousing, and executive reporting.

---

# Project Status

**Current Version:** v0.5.0

**Current Phase:** ETL Pipeline Complete — Building Power BI Dashboards

The database schema, purchase order pipeline, and receiving/inventory simulation are built, tested against a live PostgreSQL instance, and covered by an automated test suite that runs on every push via GitHub Actions. Current work is building the Power BI layer on top of the reporting views in `sql/views/`.

---

# Vision

Project Atlas aims to demonstrate an end-to-end analytics platform capable of supporting operational and executive decision-making across a fictional distribution company.

The platform will model:

- Supplier Management
- Procurement
- Purchase Orders
- Receiving Operations
- Warehouse Management
- Inventory Tracking
- Inventory Reconciliation
- Executive Reporting
- Business Intelligence
- Data Quality Monitoring

---

# Technology Stack

| Layer | Technology | Status |
|---------|------------|--------|
| Database | PostgreSQL | Built |
| ETL | Python + Pandas + SQLAlchemy | Built |
| Testing / CI | pytest + GitHub Actions | Built |
| Analytics | SQL | Built |
| Visualization | Power BI | In progress |
| Version Control | Git & GitHub | Built |
| Cloud | AWS RDS | Planned |
| Data Warehouse | Snowflake | Planned |
| Analytics Engineering | dbt | Planned |

---

# Core Business Questions

Each question below is answered by a specific, tested query -- not aspirational, these all run against real (synthetic) data today:

| Business Question | Answered by |
|---|---|
| Which products are at risk of stockout? | `sql/queries/01_stockout_risk.sql` |
| Which suppliers consistently deliver late? | `sql/queries/02_supplier_delivery_performance.sql` |
| Which purchase orders remain partially received? | `sql/queries/03_open_purchase_orders.sql` |
| Which warehouses experience receiving bottlenecks? | `sql/queries/04_receiving_bottlenecks.sql` |
| Where are inventory discrepancies occurring? | `sql/queries/05_inventory_discrepancies.sql` |

---

# Repository Structure

```
project-atlas/
├── sql/
│   ├── schema/          # DDL: tables, constraints, indexes
│   ├── migrations/      # Post-launch schema changes (001: receiving detail + inventory ledger)
│   ├── seed/            # Master data (suppliers, products, warehouses, inventory)
│   ├── queries/         # Analytical queries answering the business questions above
│   └── views/           # Power BI-facing reporting views (vw_*)
├── python/
│   ├── config/          # DB settings, supplier/warehouse reliability profiles
│   ├── etl/             # generate -> validate -> load pipeline (POs and receiving)
│   ├── validation/      # Data quality rule checks + quality log generation
│   ├── tests/           # pytest suite (17 tests, runs in CI)
│   └── utils/           # DB connection helper
├── .github/workflows/   # CI: runs pytest on every push
└── docs/                 # Business requirements, architecture decisions, changelog
```

---

# Getting Started

Requires PostgreSQL and Python 3.12+.

**1. Build the database:**
```
psql -d your_db -f sql/schema/01_database_setup.sql
psql -d your_db -f sql/schema/02_constraints.sql
psql -d your_db -f sql/schema/03_indexes.sql
psql -d your_db -f sql/migrations/001_receiving_detail_and_inventory_ledger.sql
psql -d your_db -f sql/seed/01_suppliers.sql
psql -d your_db -f sql/seed/02_products.sql
psql -d your_db -f sql/seed/03_warehouses.sql
psql -d your_db -f sql/seed/05_inventory.sql
```

**2. Set up Python and configure `.env`:**
```
cd python
pip install -r requirements.txt
cp .env.example .env   # fill in your DB credentials
```

**3. Run the full pipeline:**
```
python -m etl.generate_data
python -m validation.run_validation
python -m etl.generate_receiving_raw
python -m validation.run_receiving_validation
python -m etl.load
python -m etl.load_receiving
```

**4. Run the tests:**
```
pytest
```

All ETL steps are idempotent -- re-running them is safe and won't duplicate data.

---

# Documentation

The documentation is organized into four major areas:

- Project
- Business
- Architecture

Business Layer

↓

Master Data

↓

Transaction Data

↓

Analytical Data

↓

Power BI

- Development

Each document represents an artifact commonly produced during enterprise software and analytics projects.

---

# Roadmap

Project Atlas evolves through several major versions:

- [x] Version 0.1 — Project Foundation
- [x] Version 0.2 — Business Design
- [x] Version 0.3 — Database Architecture
- [x] Version 0.4 — Data Generation
- [x] Version 0.5 — ETL Development (PO pipeline + receiving/inventory simulation, tested end-to-end, CI passing)
- [ ] Version 0.6 — Power BI Dashboards *(in progress)*
- [ ] Version 0.7 — Cloud Deployment
- [ ] Version 1.0 — Enterprise Analytics Platform

---
# Versioning

Project Atlas follows Semantic Versioning (SemVer).

Version format:

MAJOR.MINOR.PATCH

Example:

1.4.2

- MAJOR — Significant architectural or platform milestones.
- MINOR — New functionality, project phases, or major documentation additions.
- PATCH — Bug fixes, documentation updates, refactoring, or small improvements.

Current Version:

v0.5.0

---

# Disclaimer

Project Atlas is an original portfolio project inspired by general supply chain and warehouse operations.

All business processes, datasets, database designs, and source code are independently created for educational and portfolio purposes and do not contain proprietary information from any employer.