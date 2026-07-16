# Changelog

All notable changes to Project Atlas are documented in this file.

This project follows Semantic Versioning principles.

---

## [0.5.0] - ETL Pipeline Complete

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

- 17 pytest unit tests covering every validator
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

## [0.1.0] - Repository Foundation

### Added

#### Repository Foundation
...

#### Business Documentation
...

#### Architecture Documentation
...

#### SQL Documentation
...

#### ETL Documentation
...

#### Business Intelligence Documentation
...

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

### Planned for v0.2.0

- Complete Business Analysis
- Build ER Diagram
- Build Data Dictionary
- Design relational database