# Non-Functional Requirements

## Purpose

This document defines the quality attributes and operational constraints for Project Atlas. Functional requirements describe what the platform does; non-functional requirements define how reliably, securely, maintainably, and transparently it must do it.

The requirements below are calibrated to the current portfolio implementation. They do not claim production-scale availability, security, or performance that has not been demonstrated.

---

## Status Definitions

| Status | Meaning |
|---|---|
| Implemented | Current evidence satisfies the stated acceptance criteria. |
| Partially Implemented | Controls exist, but one or more criteria or verification methods remain incomplete. |
| Planned | The quality attribute requires capabilities not present in the current architecture. |

---

## Requirements Summary

| ID | Quality Attribute | Priority | Status |
|---|---|---|---|
| `ATLAS-NFR-001` | Data integrity | High | Implemented |
| `ATLAS-NFR-002` | Idempotent processing | High | Implemented |
| `ATLAS-NFR-003` | Transactional consistency | High | Implemented |
| `ATLAS-NFR-004` | Reproducibility | High | Implemented |
| `ATLAS-NFR-005` | Auditability and observability | High | Partially Implemented |
| `ATLAS-NFR-006` | Testability and CI | High | Partially Implemented |
| `ATLAS-NFR-007` | Maintainability | High | Implemented |
| `ATLAS-NFR-008` | Security and secret handling | High | Partially Implemented |
| `ATLAS-NFR-009` | Portability | Medium | Partially Implemented |
| `ATLAS-NFR-010` | Performance | Medium | Partially Implemented |
| `ATLAS-NFR-011` | Recoverability | High | Partially Implemented |
| `ATLAS-NFR-012` | Scalability | Medium | Planned |
| `ATLAS-NFR-013` | Reporting usability | High | Partially Implemented |
| `ATLAS-NFR-014` | Documentation and traceability | High | Partially Implemented |
| `ATLAS-NFR-015` | Data privacy and portfolio safety | High | Implemented |

---

## ATLAS-NFR-001 — Data Integrity

### Requirement

The platform shall preserve valid relationships, controlled values, and quantity invariants across operational and reporting data.

### Acceptance Criteria

- Primary and foreign keys enforce entity relationships.
- Unique constraints prevent duplicate PO numbers, duplicate warehouse-product balances, and duplicate receiving events.
- Check constraints reject invalid statuses, dates, costs, and quantities.
- Receiving outcomes reconcile to gross received quantity.
- Current inventory balances reconcile to the transaction ledger.
- Power BI reads curated views rather than independently joining transactional tables.

### Verification

- Review `sql/schema/02_constraints.sql` and migration constraints.
- Run validation tests.
- Reconcile reporting-view results to operational tables.

### Status Note

Implemented for the current schema and pipeline. Known mismatches between Python rules and PostgreSQL constraints are documented in `DATA_QUALITY_RULES.md` and should be resolved before production use.

---

## ATLAS-NFR-002 — Idempotent Processing

### Requirement

Re-running a completed ETL load with the same source batch shall not duplicate purchase orders, receiving events, opening balances, or receipt ledger movements.

### Acceptance Criteria

- Existing PO numbers are skipped during PO loading.
- Existing `(po_line_id, event_number)` pairs are skipped during receiving loading.
- One opening balance is permitted per warehouse-product pair.
- Inventory balances are fully recomputed from ledger history rather than incremented from the prior snapshot.
- A repeated run produces the same database state for the same input batch.

### Verification

Execute the full load twice and compare row counts, business keys, ledger totals, and inventory balances after each run.

### Status Note

Implemented and previously verified against PostgreSQL. Automated integration coverage for this behavior remains a testing gap under `ATLAS-NFR-006`.

---

## ATLAS-NFR-003 — Transactional Consistency

### Requirement

Database load stages shall commit a logically complete unit of work or roll back that unit when an exception occurs.

### Acceptance Criteria

- Purchase order header and line loading occurs inside a SQLAlchemy transaction.
- Receiving insert, ledger movement, and balance recomputation occur inside one transaction.
- A database exception prevents a partial commit within the active loader stage.
- Referential-integrity constraints remain enabled during loading.

### Implementation Evidence

- `engine.begin()` usage in `python/etl/load.py`
- `engine.begin()` usage in `python/etl/load_receiving.py`

---

## ATLAS-NFR-004 — Reproducibility

### Requirement

The development pipeline shall produce repeatable synthetic datasets and validation results from unchanged code and configuration.

### Acceptance Criteria

- Faker and Python random generation use a documented seed.
- Raw generator runs overwrite their output files instead of silently appending.
- Validation logs are regenerated from the current source files.
- Python dependencies and supported Python version are declared.

### Implementation Evidence

- Random seed `42` in the PO and receiving generators
- `python/requirements.txt`
- Python 3.12 GitHub Actions configuration

---

## ATLAS-NFR-005 — Auditability and Observability

### Requirement

The platform shall provide enough evidence to explain which source records were rejected, why they were rejected, and how accepted inventory reached its current balance.

### Acceptance Criteria

- Data-quality issues identify record, rule, field, value, and description.
- Receiving events remain linked to their purchase order lines.
- Receipt ledger entries reference their receiving event.
- Inventory movements retain type, date, quantity delta, and notes.
- Pipeline executions record run identifier, start/end time, row counts, status, and error details.
- Historical quality results remain available after later runs.

### Current Status

Partially implemented. Record-level quality logs and the inventory ledger provide useful traceability, but CSV quality logs are overwritten. There is no durable run-history table, batch identifier, execution timestamp, centralized logging, or historical issue retention.

---

## ATLAS-NFR-006 — Testability and Continuous Integration

### Requirement

Core transformation and validation logic shall be testable without manual dashboard inspection, and automated checks shall run on repository changes.

### Acceptance Criteria

- Validator functions are isolated and return deterministic issue structures.
- Unit tests cover passing and failing rule behavior.
- GitHub Actions runs tests on pushes and pull requests to `main`.
- New validators require corresponding tests.
- Database integration tests verify constraints, key resolution, rollback, idempotency, and ledger reconciliation.
- Reporting tests validate view grain and KPI totals.

### Current Status

Partially implemented. Seventeen validator unit tests run in CI. Database loaders, migrations, reporting views, and full pipeline behavior are not yet covered by automated integration tests.

---

## ATLAS-NFR-007 — Maintainability

### Requirement

The repository shall separate business documentation, schema objects, ETL stages, validation rules, reporting contracts, tests, and presentation assets so each concern can change without unnecessary duplication.

### Acceptance Criteria

- SQL schema, constraints, indexes, migrations, seeds, queries, and views remain modular.
- Python configuration, generation, validation, loading, tests, and database utilities remain separated.
- Shared clean-row behavior has one implementation used by every dependent stage.
- Naming follows documented lowercase snake-case conventions for database objects and Python modules.
- Breaking reporting-view changes trigger corresponding Power BI and documentation updates.

### Implementation Evidence

- Functional repository structure
- `python/etl/clean_rows.py`
- Modular SQL files
- Architecture decisions and reporting-view change-control documentation

---

## ATLAS-NFR-008 — Security and Secret Handling

### Requirement

Database credentials shall remain outside source-controlled code, and database connections shall support encrypted transport where required.

### Acceptance Criteria

- Credentials are loaded from environment variables or a local `.env` file.
- `.env` files are excluded by `.gitignore`.
- A safe `.env.example` documents required configuration without real credentials.
- Cloud or production environments can require SSL.
- Logs and documentation do not expose passwords or connection strings.
- Production secrets are stored in a managed secret service rather than repository files.

### Current Status

Partially implemented. Environment-based configuration, `.gitignore`, `.env.example`, and configurable `DB_SSLMODE` are present. Managed secret storage, credential rotation, least-privilege database roles, and security scanning are not implemented.

---

## ATLAS-NFR-009 — Portability

### Requirement

A developer shall be able to run Project Atlas on a supported workstation using PostgreSQL and Python without modifying application source code.

### Acceptance Criteria

- Connection settings are environment-driven.
- Dependencies are declared in one requirements file.
- Setup and run order are documented.
- PostgreSQL-specific behavior is identified.
- A containerized environment can reproduce the database and Python runtime consistently.

### Current Status

Partially implemented. Configuration and setup instructions support manual local installation, but no Docker image, Compose environment, lock file, or automated database bootstrap exists.

---

## ATLAS-NFR-010 — Performance

### Requirement

The platform shall complete development-scale ETL and reporting operations within practical interactive time and avoid unnecessary full-table join cost on common lookups.

### Acceptance Criteria

- Foreign-key and business lookup columns used by ETL and analytics are indexed where justified.
- Power BI queries flattened reporting views rather than reconstructing operational joins.
- ETL uses batch insertion where practical.
- Performance targets are defined for source volume, load duration, view refresh, and dashboard response time.
- Query plans are reviewed before claiming enterprise scalability.

### Current Status

Partially implemented. Strategic indexes and flattened views exist, but the project has no formal performance baseline, load-volume test, query-plan evidence, or dashboard response-time target.

Suggested development targets for a future benchmark:

| Operation | Proposed Target |
|---|---|
| Validate 10,000 source rows | Under 10 seconds on a documented workstation |
| Load 10,000 clean rows | Under 30 seconds on local PostgreSQL |
| Execute each reporting view | Under 2 seconds at documented test volume |
| Render a Power BI page after data load | Under 5 seconds |

These are proposed targets, not verified current performance claims.

---

## ATLAS-NFR-011 — Recoverability

### Requirement

The platform shall support safe recovery from failed or interrupted batch processing without requiring manual deletion of partially loaded business data.

### Acceptance Criteria

- Loader exceptions roll back their active transaction.
- Missing prerequisites stop a stage with an actionable error.
- Corrected source data can be revalidated and reloaded safely.
- Database backup and restore procedures are documented and tested.
- Pipeline run state identifies the last successful stage.

### Current Status

Partially implemented. Transaction rollback, prerequisite checks, and idempotent reload behavior support development recovery. Backup/restore testing, checkpoints, and persisted run state are not implemented.

---

## ATLAS-NFR-012 — Scalability

### Requirement

The architecture shall support future growth in source volume, warehouse count, product count, transaction history, and reporting complexity without invalidating core business definitions.

### Planned Acceptance Criteria

- Incremental extraction and loading replace full-batch processing where needed.
- Reference-data validation no longer relies on static Python sets.
- Large inserts use efficient bulk-loading patterns.
- Historical analytics move to a dimensional warehouse when operational views no longer meet scale requirements.
- Partitioning, materialization, and orchestration decisions are based on measured bottlenecks.

### Current Status

Planned. The current implementation is appropriate for a portfolio-scale synthetic dataset; enterprise scalability has not been load tested and must not be claimed.

---

## ATLAS-NFR-013 — Reporting Usability

### Requirement

Dashboard users shall be able to understand each metric, recognize exceptions, and investigate summary results without reading SQL source code.

### Acceptance Criteria

- Visual titles use accurate business language.
- Metric grain and denominator are unambiguous.
- Cards use explicit measures instead of accidental implicit aggregation.
- Risk is communicated through labels and sort order as well as color.
- Detail tables support investigation and sorting.
- Dashboard results reconcile to SQL views.

### Current Status

Partially implemented. The three-page report exists, but the labeling, missing cards, sort behavior, and two warehouse charts identified in `DASHBOARD_REQUIREMENTS.md` must be corrected before version 0.6 is complete.

---

## ATLAS-NFR-014 — Documentation and Traceability

### Requirement

Every implemented capability shall be traceable from business need to requirement, business rule, schema or ETL implementation, test evidence, reporting contract, and release history.

### Acceptance Criteria

- Functional and non-functional requirements use stable IDs and implementation status.
- Business rules distinguish implemented controls from future scope.
- Schema, ETL, data-quality, view, KPI, and dashboard documentation match executable assets.
- Significant changes update the changelog.
- Learning entries explain technical decisions and corrections, not only completed tasks.
- Placeholder files do not imply implemented documentation.

### Current Status

Partially implemented. The core functional, non-functional, ETL, data-quality, SQL-view, KPI, dashboard, changelog, and learning documents are now substantive. Several older business and architecture documents still describe implemented features as future work and require reconciliation.

---

## ATLAS-NFR-015 — Data Privacy and Portfolio Safety

### Requirement

Project Atlas shall use fictional business entities and synthetic operational data so the repository can be shared publicly without exposing employer, customer, or personal information.

### Acceptance Criteria

- Company, suppliers, products, employees, and transactions are fictional or synthetic.
- No employer-specific process, proprietary dataset, or confidential logic is included.
- Local credentials are excluded from repository history and distributable archives.
- Documentation identifies the project as an independent portfolio simulation.

### Status Note

Implemented for the current project scope. This control must be reviewed whenever new datasets or screenshots are added.

---

## Non-Functional Verification Matrix

| Verification Activity | Requirements Covered | Current Automation |
|---|---|---|
| Validator unit tests | `NFR-001`, `NFR-004`, `NFR-006` | Automated in CI |
| Fresh database build | `NFR-001`, `NFR-009`, `NFR-011` | Manual |
| Repeat-load comparison | `NFR-002`, `NFR-003`, `NFR-011` | Manual |
| Ledger-to-balance reconciliation | `NFR-001`, `NFR-005` | Manual |
| Reporting-view reconciliation | `NFR-001`, `NFR-010`, `NFR-013` | Manual |
| Secret and archive review | `NFR-008`, `NFR-015` | Manual |
| Performance benchmark | `NFR-010`, `NFR-012` | Not implemented |
| Backup and restore test | `NFR-011` | Not implemented |

Non-functional status should change only when there is evidence. Architecture intent, a placeholder, or a planned tool does not satisfy a quality requirement by itself.