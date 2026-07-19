# Changelog

All notable changes to Project Atlas are documented in this file.

This project follows Semantic Versioning principles.

---

## [Unreleased]

### Documentation

- Replaced the placeholder ETL design with the implemented purchase order, receiving, and inventory-ledger workflow, including dependencies, failure behavior, and rerun guarantees.
- Added the complete Python and PostgreSQL data-quality rule catalog, quarantine behavior, test coverage, and known control gaps.
- Documented all three Power BI-facing SQL views, their grain, field semantics, and interpretation boundaries.
- Rebuilt the Power BI requirements around the three pages in `ProjectAtlas.pbix` and recorded the remaining version 0.6 acceptance gaps.
- Added an implementation-aligned KPI catalog with executable DAX examples and explicit metric limitations.
- Corrected README setup order, added reporting-view deployment commands, and replaced the stale documentation overview.
- Added implementation-aligned functional and non-functional requirements with stable IDs, acceptance criteria, status, evidence, and explicitly deferred scope.
- Rebuilt the learning log as a milestone-based engineering journal covering schema design, ETL, validation, idempotency, CI, reporting grain, and documentation governance.

### Added

- `python/.env.example` with the supported PostgreSQL connection settings.

---

## [0.5.0] - 2026-07-16 - ETL Pipeline Complete

### Added

#### Purchase Order Pipeline

- `generate_data.py` -- synthetic PO header/line generator with ~15% deliberate defect injection
- `run_validation.py` -- 10 validators (duplicate POs, missing/unknown suppliers, bad date logic, negative quantities, over-receipts, unknown SKUs, invalid cost) writing an auditable data quality log
- `load.py` -- loads only clean rows into PostgreSQL, resolving business keys to surrogate IDs; idempotent (safe to re-run)

#### Receiving & Inventory Ledger

- `sql/migrations/001_receiving_detail_and_inventory_ledger.sql` -- adds accepted/damaged/rejected quantity breakdown to `receiving_transactions`, and a new `inventory_transactions` ledger table (opening balance + movements, not a hand-edited snapshot)
- `python/config/profiles.py` -- supplier and warehouse reliability profiles (on-time %, damage %, rejection %) driving differentiated, realistic receiving behavior per supplier
- `generate_receiving_raw.py` -- derives 1-2 receiving events per PO line from supplier profiles; sourced entirely from raw CSVs, no DB dependency at generation time
- `run_receiving_validation.py` -- 5 receiving-specific validators (quantity math, bad dates, unknown warehouse, duplicate events)
- `load_receiving.py` -- loads clean events, writes ledger entries, recomputes `inventory_balances` from the full ledger on every run (idempotent)
- `python/etl/clean_rows.py` -- shared clean-row filtering logic used by both `load.py` and `generate_receiving_raw.py`, so the two can't drift on what "clean" means

#### Testing & CI

- 17 pytest unit tests covering purchase order and receiving validation behavior
- GitHub Actions workflow running the full test suite on every push
- `pytest.ini` (`pythonpath = .`) so tests run identically from CI, terminal, and IDE test runners

#### Analytics

- 5 analytical queries answering every business question in this README
- 3 Power BI-facing reporting views (`vw_supplier_performance`, `vw_inventory_status`, `vw_receiving_performance`)

### Fixed

- `purchase_orders` was missing its `order_date` column despite constraints, indexes, and seed data all referencing it -- schema would have failed on first real build
- No unique constraint existed on `po_number` even though the validator suite assumed one (`SCHEMA-uq_po_number`) -- duplicate POs could have been silently inserted
- Opening-balance seeding originally re-derived from the mutable `inventory_balances` table instead of the immutable ledger, causing silent double-counting on repeated pipeline runs -- fixed by anchoring the check to `inventory_transactions` itself
- CI initially ran bare `pytest`, which doesn't add the working directory to `sys.path` the way `python -m pytest` does -- caused every CI run to fail on import even though local testing passed

### Verified

- Full pipeline (schema → migration → seed → generate → validate → load, both PO and receiving) tested against a completely fresh PostgreSQL database
- All load scripts confirmed idempotent -- re-running any of them produces identical results

---

## [0.1.0] - 2026-07-07 - Repository Foundation

### Added

#### Repository Foundation

- Created the Project Atlas GitHub repository.
- Established the functional directory structure for SQL, Python, Power BI, data, diagrams, documentation, and GitHub workflows.
- Configured semantic versioning, changelog practices, and placeholder preservation for empty directories.

#### Business Documentation

- Defined the fictional Atlas Distribution Company and the project's business context.
- Added product vision, business requirements, stakeholders, success metrics, process flows, events, and initial business rules.
- Established requirement and business-rule ID conventions using the `ATLAS-` prefix.

#### Architecture Documentation

- Added the initial system architecture, ERD, data dictionary, data classification, and architecture decision records.
- Documented the separation between master, transactional, analytical, and reporting data.
- Established the layered PostgreSQL → Python ETL → SQL views → Power BI architecture.

#### SQL Documentation

- Added the initial PostgreSQL schema, constraint, index, and seed-data structure.
- Separated database objects into modular deployment scripts.
- Added documentation locations for schema, indexes, views, and future stored procedures.

#### ETL Documentation

- Established documentation locations for ETL design and data-quality controls.
- Defined the planned raw → validate → transform → load workflow.

#### Business Intelligence Documentation

- Added the initial dashboard requirements and KPI catalog structure.
- Defined Power BI as the presentation layer over curated SQL views.

#### Development Environment

- Configured Git
- Configured GitHub
- Configured VS Code
- Completed first Git commit and push
- Added `.gitkeep` placeholders

---

### Changed

- Renamed Inventory Ledger to Inventory Balances.
- Reorganized SQL schema into modular components.
- Standardized documentation structure.

---

### Planned Next

- Complete Business Analysis
- Build ER Diagram
- Build Data Dictionary
- Design relational database