---

# `ROADMAP.md`

# Project Atlas Roadmap

## Version 0 — CS-499 Capstone Foundation

Completed academic inventory management system using Android, Kotlin, MVVM, Room, DAO layers, repository pattern, LiveData, and secure coding practices.

## Version 1 — PostgreSQL + SQL Foundation

Goal: Build the operational database layer.

Planned work:
- Design relational schema
- Create suppliers, products, warehouses, inventory, purchase orders, transactions, receiving, and shipments tables
- Add primary keys and foreign keys
- Add constraints
- Create sample data
- Write analytical SQL queries

## Version 2 — Python ETL + Data Quality

Goal: Automate data generation, loading, cleaning, and validation.

Planned work:
- Generate realistic supply chain data
- Import data into PostgreSQL
- Detect duplicate records
- Flag missing values
- Identify negative inventory
- Validate purchase order and receiving dates
- Create data quality issue logs

## Version 3 — Power BI Dashboards

Goal: Build business-facing dashboards.

Planned dashboards:
- Executive Inventory Dashboard
- Warehouse Operations Dashboard
- Procurement Dashboard
- Supplier Performance Dashboard
- Inventory Discrepancy Dashboard

## Version 4 — Cloud Deployment

Goal: Move the database from local PostgreSQL to a cloud-hosted environment.

Planned tools:
- AWS RDS PostgreSQL or Supabase
- Power BI cloud connection
- Scheduled refresh process

## Version 5 — Data Warehouse + Analytics Engineering

Goal: Redesign Atlas using modern analytics engineering practices.

Planned tools:
- Snowflake
- dbt
- Dimensional modeling
- Staging models
- Fact tables
- Dimension tables
- Data tests

## Version 6 — Production Polish

Goal: Make Atlas interview-ready.

Planned work:
- Final README
- Architecture diagram
- Data dictionary
- Dashboard screenshots
- LinkedIn article
- Resume bullets
- Interview guide
