# Project Atlas Learning Log

## Purpose

This log records the technical judgment developed while building Project Atlas. It connects coursework and certifications to implementation, but its main purpose is to explain what I learned by designing, breaking, testing, and correcting an end-to-end data platform.

The log focuses on evidence:

- What problem I was trying to solve
- What technical concept I applied
- What failed or changed my understanding
- What I implemented in the repository
- Why the decision matters to the business

This makes the log useful for project retrospectives, portfolio reviews, and technical interviews rather than serving as a list of completed courses.

---

## Foundation-to-Project Mapping

| Learning Foundation | Concepts Applied to Atlas | Repository Evidence |
|---|---|---|
| B.S. Computer Science | System decomposition, secure configuration, data structures, testing, version control | Layered architecture, modular repository, Python modules, CI |
| CS-499 Inventory Capstone | Inventory domain, data access patterns, input validation, separation of concerns | Evolution from mobile inventory application to supply-chain data platform |
| Google Data Analytics Certificate | Business-question framing, data cleaning, KPI definition, dashboard design | Business requirements, quality logs, analytical queries, KPI catalog |
| SQL Associate Foundations | Joins, aggregation, constraints, indexes, analytical SQL | PostgreSQL schema, reporting views, business-question queries |
| Current Data Engineering Study | ETL design, data quality, reproducibility, idempotency, operational data modeling | Python pipeline, validation framework, inventory ledger, CI |
| Current Power BI Practice | Grain, filter context, aggregation, visual design, metric governance | Three-page PBIX report, dashboard requirements, explicit DAX definitions |

---

## Core Engineering Lessons

### Business Context Must Constrain Technical Design

Tables and dashboards are not valuable merely because they exist. Every implemented object should answer a business question or enforce a documented rule. Atlas therefore starts with procurement, receiving, inventory, and reporting problems before selecting schema objects or visual types.

### Data Grain Must Be Declared Before Metrics

Several metrics can be technically valid while answering different questions. A count of inventory-view rows is a count of warehouse-SKU positions, not necessarily a count of unique products. A count of receiving rows is a count of events, not purchase orders. Declaring grain first prevents misleading KPI labels.

### Idempotency Requires Evidence

Calling a script "safe to rerun" is not enough. Idempotency depends on stable business keys, uniqueness controls, transaction boundaries, and balance reconstruction. The opening-balance defect proved that a pipeline can appear correct on the first run and silently corrupt totals on the second.

### Validation and Constraints Serve Different Purposes

Python validation creates understandable issue evidence before loading. PostgreSQL constraints protect the system of record. Both are necessary, but their rules must agree. If Python permits a value that PostgreSQL rejects—or rejects a value PostgreSQL permits—the pipeline has an undocumented control gap.

### Documentation Is Part of the Data Contract

Stale documentation is not harmless. If a document calls an implemented ledger "future," labels planned lead-time variance as delivery performance, or describes dashboards that do not exist, it teaches reviewers the wrong architecture. Documentation must be verified against executable assets just like code.

---

## Development Journal

## July 6, 2026 — Project Foundation and Business Framing

### Milestone

Converted the CS-499 inventory capstone concept into a new enterprise-style supply-chain analytics project.

### Problem

The original academic application demonstrated software-development skills but did not show how operational data could move through a modern analytics platform. I needed a project structure that could support business analysis, PostgreSQL, Python ETL, data quality, SQL analytics, and Power BI without becoming one unorganized code folder.

### What I Learned

- Repository structure communicates architecture before anyone reads the code.
- A portfolio project becomes more credible when its fictional business, users, problems, and success criteria are explicit.
- Requirements and business rules should use stable identifiers so implementation can be traced later.
- Version history matters because the story of how the system evolved is part of the engineering evidence.

### Applied to Atlas

- Created the repository and major functional directories.
- Defined Atlas Distribution Company, the product vision, stakeholders, and initial business requirement.
- Established the `ATLAS-BR`, `ATLAS-FR`, `ATLAS-NFR`, and `ATLAS-RULE` naming approach.
- Added semantic versioning, roadmap, changelog, and learning-log practices.

### Business Impact

The project gained a clear decision-making purpose: improve inventory visibility, supplier analysis, receiving quality, and warehouse reporting across a fictional multi-warehouse distributor.

### Reflection

My first instinct was to prove technical skill by building quickly. The stronger approach was to define what the platform was supposed to accomplish and then make the technical layers answer those needs. The lesson was not "documentation before code at any cost"; it was that implementation without a business contract becomes a collection of disconnected demos.

---

## July 7–8, 2026 — Relational Modeling and Modular PostgreSQL Design

### Milestone

Designed the normalized operational database and separated schema, constraints, indexes, seed data, and architecture documentation.

### Problem

Inventory, purchase orders, receiving, products, suppliers, warehouses, employees, and departments have different lifecycles. Combining them carelessly would create duplicate data, inconsistent relationships, and reporting logic that could not be trusted.

### What I Learned

- Surrogate keys simplify internal relationships, while business keys remain essential for ETL matching.
- PostgreSQL does not automatically index every foreign key, so indexes must reflect actual joins and filters.
- `ON DELETE` behavior is a business decision: transactional history should generally restrict deletion of referenced master data.
- Current balances and movement history are different concepts and require different controls.
- Schema scripts and migrations serve different purposes; destructive setup scripts should not be described as idempotent migrations.

### Applied to Atlas

- Created normalized master and transactional tables.
- Added foreign keys, uniqueness rules, controlled statuses, date checks, and quantity constraints.
- Added indexes for SKU lookup, PO joins, date filtering, department/warehouse relationships, and warehouse-product balances.
- Added architecture, ERD, data dictionary, data classification, and decision records.
- Added environment-driven PostgreSQL configuration and a shared SQLAlchemy engine helper.

### Challenge and Correction

The original `purchase_orders` table did not contain `order_date` even though constraints, indexes, and seed data referenced it. The schema looked documented but would have failed during a fresh build. I added the missing field and learned that DDL modules must be tested together in deployment order—not reviewed as isolated files.

### Business Impact

Database controls moved critical rules closer to the data. Invalid relationships and impossible values could no longer depend solely on application discipline.

### Reflection

Database design is not just drawing an ERD. The real work is deciding which invariants the database can guarantee, how records behave when parent data changes, and how operational transactions will support later analytics.

---

## July 9, 2026 — Synthetic Data, Validation, and Quarantine

### Milestone

Built the first Python-generated purchase order extracts, validation functions, quality logs, and unit tests.

### Problem

Perfect seed data cannot demonstrate data engineering. A useful pipeline needs realistic defects, deterministic reproduction, understandable validation results, and a clear rule for which records can proceed.

### What I Learned

- Synthetic data should be realistic enough to support business analysis and intentionally imperfect enough to test controls.
- Source extracts should use business keys rather than internal database IDs.
- Validation functions are easier to test when they return issue records instead of mutating DataFrames.
- Reproducible random seeds make defects debuggable and tests repeatable.
- A data-quality log is more useful than a pass/fail flag when it identifies the record, rule, field, value, and explanation.

### Applied to Atlas

- Generated purchase order headers and lines with deterministic Faker/random seeds.
- Injected duplicate keys, missing suppliers, invalid dates, bad quantities, unknown SKUs, and invalid cost scenarios.
- Created reusable validator functions and CSV quality logs.
- Added initial pytest coverage.
- Declared Python dependencies and reorganized raw and processed data paths.

### Challenge and Correction

I learned that "flagging bad rows" is incomplete if dependent records remain. A clean-looking line cannot be loaded when its parent PO header is rejected. This led to a shared clean-row contract that excludes invalid headers and their dependent lines consistently.

### Business Impact

The pipeline could demonstrate how operational defects are identified before they reach procurement and inventory reporting.

### Reflection

Data cleaning should not silently erase evidence. Keeping raw data and producing a separate quarantine manifest creates a clearer audit trail and makes the pipeline easier to explain.

---

## July 16, 2026 — End-to-End ETL, Receiving Quality, and Inventory Ledger

### Milestone

Completed the purchase order and receiving pipelines, introduced event-level quality outcomes, derived inventory from a ledger, added analytical views and queries, and stabilized CI.

### Problem

The project had purchase order data, but it did not yet model how partial deliveries, damaged units, rejected units, and accepted inventory should affect warehouse balances. A mutable quantity snapshot alone could not explain why a balance changed.

### What I Learned

- Receiving must be modeled at event grain because one PO line can arrive across multiple shipments.
- Gross received quantity is not the same as accepted inventory.
- Damaged and rejected units belong in receiving history but must not increase sellable stock.
- An append-only ledger provides better traceability than directly editing a balance.
- A derived balance is safer when recomputed from immutable movements than incrementally added to an already-derived snapshot.
- Shared transformation logic prevents downstream stages from developing different definitions of "clean."
- CI failures can reveal environment assumptions hidden by a local IDE or shell.

### Applied to Atlas

- Added supplier and warehouse reliability profiles.
- Generated one or two receiving events per eligible PO line.
- Added accepted, damaged, and rejected quantity validation.
- Added `inventory_transactions` with opening-balance and receipt movements.
- Updated `inventory_balances` through full ledger recomputation.
- Added idempotent checks for existing PO numbers and receiving events.
- Added five business-question queries and three Power BI reporting views.
- Expanded the suite to 17 validator tests and ran it in GitHub Actions.

### Critical Defect Found

The first opening-balance approach used the current `inventory_balances` snapshot as its source on later runs. Once that table had already been recomputed from the ledger, treating it as a new opening balance would double-count inventory. I changed the guard so a balance is seeded only when the warehouse-product pair has no ledger history.

### CI Lesson

Tests passed locally but initially failed in GitHub Actions because bare `pytest` did not resolve the project imports the same way as `python -m pytest`. Adding `pytest.ini` and using a consistent module invocation removed the environment-specific behavior.

### Business Impact

Inventory became explainable: opening quantity plus accepted receiving movements equals current on-hand quantity. Receiving quality could be analyzed without inflating stock, and the same validated datasets could feed business-facing views.

### Reflection

This milestone changed the project from a database exercise into a real data-engineering story. The strongest evidence is not that the scripts run once; it is that the data model explains operational events, invalid rows are controlled, repeated loads do not corrupt totals, and reporting fields have traceable origins.

---

## July 19, 2026 — Power BI Grain, KPI Governance, and Documentation Reconciliation

### Milestone

Reviewed the Power BI file and repository documentation against the implemented SQL and Python assets.

### Problem

The repository had working reporting views and a three-page Power BI report, but several documentation files were placeholders or described an older five-dashboard plan. Some visual labels also overstated what the current calculations measured.

### What I Learned

- A dashboard can be visually correct while still answering the wrong business question.
- Counting inventory-view rows measures warehouse-SKU positions, not distinct products.
- Averaging supplier-level averages creates an unweighted result; it is not automatically a company-wide weighted KPI.
- `days_late` across early and late receipts is delivery variance, not average lateness unless positive rows are filtered.
- Comparing planned delivery dates with quoted lead time is planning variance, not actual on-time delivery.
- Implicit Power BI aggregations make KPI intent harder to audit than named DAX measures.
- Documentation review should inspect the PBIX metadata, SQL view grain, and ETL lineage together.

### Applied to Atlas

- Documented the grain and field contract of all three reporting views.
- Rebuilt the KPI catalog with precise definitions and executable DAX examples.
- Replaced the obsolete dashboard scope with the three implemented pages.
- Recorded incomplete cards, labels, filters, and visual calculations as version 0.6 acceptance gaps.
- Documented the full ETL and data-quality architecture.
- Added functional and non-functional requirements with implementation status and evidence.
- Rebuilt the changelog and learning log so they reflect actual engineering milestones.

### Dashboard Corrections Identified

- Add Total Suppliers and Average Supplier Lead-Time Variance cards.
- Rename the stockout card or change it to a true distinct-product calculation.
- Sort the at-risk detail table by the deepest shortfall.
- Replace the inventory warehouse chart with at-risk-location count by warehouse.
- Filter the receiving warehouse chart to late events only.
- Keep planned supplier variance separate from actual receiving timeliness.

### Business Impact

The reporting layer now has a defensible contract. Reviewers can understand exactly what each view and KPI means, what is complete, and what remains before the Power BI phase can be released.

### Reflection

I learned that professional documentation is not about making the project sound complete. Its job is to make the truth easy to verify. Explicitly documenting incomplete controls and metric limitations makes the project stronger because it demonstrates judgment rather than overclaiming.

---

## Current Learning Priorities

### 1. Database Integration Testing

Next application goals:

- Build a temporary PostgreSQL test environment.
- Test migrations and constraints automatically.
- Verify loader rollback and key resolution.
- Run the pipeline twice and assert idempotency.
- Reconcile ledger totals to current balances.

### 2. Power BI Semantic Modeling

Next application goals:

- Replace implicit aggregations with named DAX measures.
- Finish version 0.6 acceptance gaps.
- Add a calendar dimension if time analysis expands.
- Test filter context and totals against SQL.
- Add portfolio-quality screenshots and metric explanations.

### 3. Environment Reproducibility

Next application goals:

- Add Docker and Docker Compose for PostgreSQL and Python.
- Add one command or script for local database bootstrap.
- Pin dependency versions through a reproducible lock strategy.
- Add automated environment validation.

### 4. Pipeline Observability

Next application goals:

- Create pipeline-run and data-quality issue tables.
- Add run IDs, timestamps, row counts, duration, and status.
- Preserve historical quality results.
- Separate warnings from rejected records.

### 5. Analytics Engineering

Future application goals:

- Introduce dimensional modeling only after operational reporting requirements stabilize.
- Move transformations into staged dbt models.
- Add source freshness, uniqueness, relationship, and accepted-value tests.
- Evaluate Snowflake or another warehouse based on a defined need rather than tool collection.

---

## Interview Evidence Developed Through Atlas

Project Atlas now supports concrete explanations of:

- Designing a normalized PostgreSQL operational model
- Translating business rules into constraints and validators
- Creating deterministic synthetic source data
- Quarantining invalid records without destroying raw evidence
- Resolving business keys to surrogate keys
- Modeling partial receipts and inspection outcomes
- Building an append-only inventory ledger
- Finding and correcting an idempotency defect
- Debugging a local-versus-CI import failure
- Designing reporting views with explicit grain
- Challenging misleading KPI labels and aggregations
- Maintaining traceable architecture and release documentation

These examples are stronger than a tool list because each one includes a problem, decision, implementation, failure mode, and business consequence.

---

## Entry Template

Use this structure for future milestones:

```text
## Date — Milestone

### Problem
What business or technical problem needed to be solved?

### What I Learned
What concept or engineering principle became clearer?

### Applied to Atlas
What changed in the repository?

### Challenge and Correction
What failed, changed, or disproved an assumption?

### Business Impact
Why does the change matter to a stakeholder or decision?

### Reflection
How did the work change my understanding or future approach?
```

Future entries should document meaningful decisions or corrections. Routine file creation belongs in the changelog, not the learning log.