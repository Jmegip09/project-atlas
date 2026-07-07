# Business Process Flow

## Purpose

This document defines the core operational workflow of Atlas Distribution Company.

Rather than describing software functionality, this document models how inventory moves through the business from procurement to consumption. These business processes drive the design of the database, ETL pipelines, reporting logic, and executive dashboards throughout Project Atlas.

---

# High-Level Process

Supplier
    ↓
Purchase Order Creation
    ↓
Purchase Order Approval
    ↓
Supplier Shipment
    ↓
Receiving & Inspection
    ↓
Inventory Storage
    ↓
Inventory Availability
    ↓
Warehouse Transfers (Optional)
    ↓
Inventory Consumption
    ↓
Cycle Count
    ↓
Inventory Adjustment (If Required)
    ↓
Operational Reporting
    ↓
Executive Decision Making

---

# Process Overview

Atlas Distribution Company purchases products from approved suppliers through a centralized procurement process.

Once a purchase order is approved, the supplier ships the requested inventory to the designated warehouse.

Warehouse personnel receive and inspect incoming shipments to verify quantities and identify damaged or missing items before inventory becomes available for operational use.

Available inventory may remain in storage, be transferred between warehouse locations, or be issued to internal departments based on operational demand.

Inventory accuracy is maintained through scheduled cycle counts and reconciliation activities. Any discrepancies are investigated and corrected through controlled inventory adjustment processes.

Operational data collected throughout these activities is consolidated into dashboards and reports that support business decision-making across multiple organizational levels.

---

# Core Business Events

Project Atlas models the following operational events.
---

# Process Rules

## Procurement Rules

- Only active suppliers may receive new purchase orders.
- A purchase order must have at least one purchase order line.
- A purchase order cannot be marked as fully received until all ordered quantities have been received.
- Cancelled purchase orders should not update inventory.

## Receiving Rules

- Inventory should only increase after receiving is completed.
- A received quantity cannot exceed the ordered quantity without an approved exception.
- Damaged or rejected inventory should not be added to available stock.
- Partial receipts must remain tied to the original purchase order line.

## Inventory Rules

- Inventory quantity on hand cannot be negative.
- Every inventory balance must belong to one warehouse and one product.
- Every inventory movement should create a traceable transaction record.
- Inventory transfers must decrease stock from the source warehouse and increase stock at the destination warehouse.

## Cycle Count Rules

- Cycle counts compare system quantity against counted quantity.
- Variances must generate a discrepancy record.
- Approved adjustments update inventory balances.
- Adjustment reason codes are required for auditability.

---

# Process Exceptions

Project Atlas should account for common operational exceptions, including:

- Supplier delivers late.
- Supplier delivers partial quantity.
- Supplier delivers damaged goods.
- Purchase order is cancelled.
- Inventory is received into the wrong warehouse.
- Inventory balance becomes inconsistent with transaction history.
- Cycle count identifies missing or excess stock.
- Product falls below safety stock level.
- Warehouse transfer is delayed or incomplete.

---

# Process-to-Data Mapping

| Business Event | Primary Tables / Future Tables | Reporting Impact |
|---|---|---|
| Purchase Order Created | suppliers, purchase_orders, purchase_order_lines | Open PO reporting, procurement trends |
| Supplier Ships Order | shipments | In-transit inventory, supplier lead time |
| Receiving Inspection | receiving | Receiving performance, late delivery analysis |
| Inventory Storage | inventory_balances | Quantity on hand, stock availability |
| Inventory Consumption | inventory_transactions | Usage trends, reorder planning |
| Warehouse Transfer | inventory_transactions, warehouses | Transfer tracking, warehouse balancing |
| Cycle Count | cycle_counts | Inventory accuracy, variance reporting |
| Inventory Adjustment | inventory_adjustments | Discrepancy analysis, audit trail |
| Business Reporting | SQL views, Power BI dashboards | Executive and operational KPIs |

---

# Key Business Questions Supported

This process supports analysis of questions such as:

- Which products are at risk of stockout?
- Which suppliers deliver late most often?
- Which warehouses have the highest inventory value?
- Which products have the largest inventory discrepancies?
- Which purchase orders are partially received?
- Which warehouses are experiencing receiving bottlenecks?
- How much inventory value is tied up by category?
- Are inventory adjustments increasing over time?

---

# Version 1 Scope

Version 1 will focus on:

- Suppliers
- Products
- Warehouses
- Purchase Orders
- Purchase Order Lines
- Receiving
- Inventory Balances
- Inventory Transactions
- Cycle Counts
- Inventory Adjustments
- Power BI reporting requirements

Version 1 will not include:

- Live APIs
- Real employer data
- Machine learning forecasting
- Full transportation management
- Mobile app integration
- Automated cloud deployment

## Event 1 — Purchase Order Created

Description

A buyer creates a purchase order requesting inventory from an approved supplier.

Business Outcome

Inventory replenishment process begins.

Primary Data Generated

- Purchase Order
- Supplier
- Purchase Order Lines
- Order Date

---

## Event 2 — Supplier Ships Order

Description

Supplier fulfills the purchase order and ships inventory.

Business Outcome

Inventory is in transit.

Primary Data Generated

- Shipment Date
- Expected Delivery Date
- Shipment Status

---

## Event 3 — Receiving Inspection

Description

Warehouse personnel inspect incoming inventory before acceptance.

Business Outcome

Inventory is accepted, partially accepted, or rejected.

Primary Data Generated

- Receiving Record
- Employee
- Warehouse
- Quantity Received
- Inspection Notes

---

## Event 4 — Inventory Storage

Description

Accepted inventory is placed into warehouse storage locations.

Business Outcome

Inventory becomes available for operational use.

Primary Data Generated

- Warehouse
- Bin Location
- Quantity On Hand

---

## Event 5 — Inventory Consumption

Description

Inventory is issued to satisfy operational demand.

Business Outcome

Available inventory decreases.

Primary Data Generated

- Product
- Quantity Issued
- Department Request
- Transaction Date

---

## Event 6 — Warehouse Transfer

Description

Inventory is moved between warehouse locations.

Business Outcome

Inventory availability is balanced across facilities.

Primary Data Generated

- Source Warehouse
- Destination Warehouse
- Transfer Quantity
- Transfer Date

---

## Event 7 — Cycle Count

Description

Warehouse personnel perform scheduled inventory verification.

Business Outcome

Inventory accuracy is validated.

Primary Data Generated

- Count Session
- Counted Quantity
- Variance
- Employee

---

## Event 8 — Inventory Adjustment

Description

Authorized personnel correct inventory discrepancies.

Business Outcome

Inventory balances remain accurate.

Primary Data Generated

- Adjustment Type
- Adjustment Quantity
- Reason Code
- Approval

---

## Event 9 — Business Reporting

Description

Operational data is transformed into KPIs and dashboards for decision-makers.

Business Outcome

Leadership gains visibility into operational performance.

Primary Outputs

- Executive Dashboard
- Warehouse Dashboard
- Procurement Dashboard
- Inventory Dashboard
- Supplier Performance Dashboard

---

# Business Principles

Project Atlas follows several guiding operational principles.

- Inventory accuracy is more important than inventory speed.
- Every inventory movement should be traceable.
- Procurement decisions should be supported by measurable supplier performance.
- Reporting should support business decisions, not simply display data.
- Data quality is considered a business requirement rather than a technical afterthought.

---

# Relationship to Project Atlas

This document serves as the foundation for:

- Business Requirements
- Functional Requirements
- Database Design
- Entity Relationship Diagram (ERD)
- ETL Pipelines
- Power BI Dashboards
- Data Quality Framework
