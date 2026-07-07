# Business Process Flow

## Purpose

This document describes how inventory moves through Atlas Distribution Company's supply chain.

Rather than focusing on software implementation, this document models the operational workflow that the platform is designed to support.

The business process serves as the foundation for future database design, ETL pipelines, reporting, and dashboard development.

---

# High-Level Supply Chain Process

Supplier
    ↓
Purchase Order Created
    ↓
Supplier Ships Order
    ↓
Shipment Arrives
    ↓
Receiving Inspection
    ↓
Inventory Updated
    ↓
Warehouse Storage
    ↓
Inventory Transfers (Optional)
    ↓
Internal Department Requests Inventory
    ↓
Inventory Issued
    ↓
Cycle Count
    ↓
Inventory Adjustment (If Needed)
    ↓
Executive Reporting

---

# Process Overview

The business process begins when a buyer creates a purchase order for products needed by the organization.

Once approved, the supplier fulfills the order and ships the requested items to the designated warehouse.

Upon arrival, receiving personnel inspect the shipment, verify quantities, and record any discrepancies before inventory is updated.

Inventory is then available for internal requests, transfers between warehouses, or future replenishment planning.

Inventory accuracy is maintained through periodic cycle counts and reconciliation activities.

Finally, operational data is aggregated into reporting dashboards that support decision-making across the organization.
