# Data Dictionary

## Purpose

This document defines the data elements used throughout Project Atlas.

The Data Dictionary serves as the authoritative reference for every database table, column, key, and business definition within the platform. It ensures consistent terminology across database development, ETL pipelines, SQL queries, Power BI dashboards, and project documentation.

The dictionary will continue to evolve as new entities are introduced throughout the project lifecycle.

---

# Naming Standards

Project Atlas follows the following naming conventions.

## Tables

- Use plural nouns
- Lowercase
- Snake case

Examples:

- suppliers
- products
- purchase_orders
- inventory_balances

---

## Primary Keys

Every table contains a surrogate primary key using the following convention:

```
<table>_id
```

Examples:

- supplier_id
- product_id
- warehouse_id
- po_id

---

## Foreign Keys

Foreign keys use the same name as their referenced primary key.

Examples:

- supplier_id
- warehouse_id
- product_id

---

## Dates

Date fields end with `_date`.

Examples:

- order_date
- expected_delivery_date
- last_count_date

---

## Status Fields

Status fields end with `_status`.

Examples:

- supplier_status
- po_status

---

# Master Data

## Table: suppliers

| Column | Data Type | Description |
|----------|-----------|-------------|
| supplier_id | INT | Unique supplier identifier |
| supplier_name | VARCHAR(150) | Supplier business name |
| contact_email | VARCHAR(100) | Supplier contact email |
| lead_time_days | INT | Standard supplier lead time |
| supplier_status | VARCHAR(20) | Current supplier status |

---

## Table: products

| Column | Data Type | Description |
|----------|-----------|-------------|
| product_id | INT | Unique product identifier |
| sku | VARCHAR(50) | Stock Keeping Unit |
| product_name | VARCHAR(150) | Product description |
| category | VARCHAR(50) | Product category |
| unit_of_measure | VARCHAR(10) | Inventory unit |
| safety_stock_level | INT | Minimum inventory threshold |

---

## Table: warehouses

| Column | Data Type | Description |
|----------|-----------|-------------|
| warehouse_id | INT | Unique warehouse identifier |
| warehouse_code | VARCHAR(10) | Warehouse code |
| warehouse_name | VARCHAR(100) | Warehouse name |
| location_city | VARCHAR(100) | Warehouse location |

---

# Procurement

## Table: purchase_orders

| Column | Data Type | Description |
|----------|-----------|-------------|
| po_id | INT | Purchase order identifier |
| po_number | VARCHAR(50) | Business PO number |
| supplier_id | INT | Supplier reference |
| order_date | DATE | Purchase order creation date |
| expected_delivery_date | DATE | Expected receipt date |
| po_status | VARCHAR(20) | Current PO status |

---

## Table: purchase_order_lines

| Column | Data Type | Description |
|----------|-----------|-------------|
| po_line_id | INT | Purchase order line identifier |
| po_id | INT | Parent purchase order |
| product_id | INT | Ordered product |
| quantity_ordered | INT | Ordered quantity |
| quantity_received | INT | Received quantity |
| unit_cost | DECIMAL(10,2) | Unit purchase cost |

---

# Inventory

## Table: inventory_balances

| Column | Data Type | Description |
|----------|-----------|-------------|
| inventory_id | INT | Inventory balance identifier |
| warehouse_id | INT | Warehouse reference |
| product_id | INT | Product reference |
| quantity_on_hand | INT | Current inventory quantity |
| bin_location | VARCHAR(20) | Storage location |
| last_count_date | TIMESTAMP | Last physical count |

---

## Future Tables

The following entities are planned for future releases.

### inventory_transactions

Tracks every inventory movement.

Examples:

- Receiving
- Transfers
- Consumption
- Adjustments

---

### receiving

Tracks inbound shipment inspections.

---

### cycle_counts

Stores scheduled inventory verification events.

---

### inventory_adjustments

Tracks approved inventory corrections.

---

### warehouse_transfers

Tracks inventory movement between warehouse locations.

---

# Business Definitions

## Inventory Balance

Represents the current available quantity of a product within a specific warehouse.

---

## Purchase Order

A formal request issued to a supplier for inventory replenishment.

---

## Purchase Order Line

A single product contained within a purchase order.

---

## Supplier

An approved external organization that provides products to Atlas Distribution Company.

---

## Warehouse

A physical storage location where inventory is received, stored, transferred, and issued.

---

## Safety Stock

The minimum quantity of inventory maintained to reduce stockout risk.

---

# Future Enhancements

As Project Atlas evolves, the Data Dictionary will expand to include:

- Default values
- Nullable fields
- Foreign key relationships
- Check constraints
- Business rules
- Data lineage
- ETL mappings
- Power BI semantic model mappings

---

# Relationship to Project Atlas

The Data Dictionary supports:

- Business Requirements
- Entity Relationship Diagram (ERD)
- PostgreSQL Schema
- SQL Development
- ETL Pipelines
- Data Quality Framework
- Power BI Dashboards
- Future Data Warehouse Design
```