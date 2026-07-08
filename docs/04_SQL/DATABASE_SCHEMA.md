# Database Schema

## Purpose

This document describes the physical PostgreSQL implementation of the data model defined in `ERD.md`. It covers table structure, key relationships, and the reasoning behind each design decision, so the schema can be understood without reading raw SQL.

Source of truth: `sql/schema/01_database_setup.sql`, `02_constraints.sql`, `03_indexes.sql`.

---

# Design Objectives

- Separate master (reference) data from transactional data
- Enforce referential integrity through foreign keys rather than application logic
- Use CHECK constraints to encode business rules directly in the database
- Keep every table's primary key as a surrogate `GENERATED ALWAYS AS IDENTITY` column

---

# Master Data Tables

## suppliers
Vendor records purchase orders are placed against.
- `supplier_id` (PK)
- `supplier_status` restricted to `Active`, `On Hold`, `Inactive`
- `lead_time_days` must be >= 0

## products
Product/SKU catalog.
- `product_id` (PK)
- `safety_stock_level` must be >= 0

## warehouses
Physical storage locations.
- `warehouse_id` (PK)

## departments
Organizational departments.
- `department_id` (PK)
- `department_type` restricted to a fixed set (Operations, Procurement, Inventory, Finance, IT, Executive, Support)

## employees
Staff records, tied to a department and optionally a warehouse.
- `employee_id` (PK)
- FK -> `departments(department_id)`, `ON DELETE RESTRICT` (can't delete a department that still has staff)
- FK -> `warehouses(warehouse_id)`, `ON DELETE SET NULL` (losing a warehouse shouldn't delete the employee)
- `employee_status` restricted to Active, On Leave, Inactive, Retired

---

# Transactional Tables

## purchase_orders
Header record for a PO.
- `po_id` (PK)
- FK -> `suppliers(supplier_id)`, `ON DELETE RESTRICT`
- FK -> `employees(created_by_employee_id)`, `ON DELETE SET NULL`
- `chk_delivery_date`: expected delivery can't be before the order date
- `po_status` restricted to Open, Partially Received, Fully Received, Cancelled

## purchase_order_lines
Line-item detail for a PO (one row per product on the order).
- `po_line_id` (PK)
- FK -> `purchase_orders(po_id)`, `ON DELETE CASCADE` (deleting a PO removes its lines)
- FK -> `products(product_id)`, `ON DELETE RESTRICT`
- `chk_received_vs_ordered`: `quantity_received` can never exceed `quantity_ordered`

## receiving_transactions
Individual receiving events against a PO line (a PO line can be received in multiple partial shipments).
- `receiving_id` (PK)
- FK -> `purchase_order_lines(po_line_id)`, `ON DELETE RESTRICT`
- FK -> `warehouses(warehouse_id)`, `ON DELETE RESTRICT`
- `chk_receiving_qty`: quantity received per event must be > 0

## inventory_balances
Current on-hand quantity per warehouse/product combination.
- `inventory_id` (PK)
- `uq_warehouse_product`: one row per warehouse + product pair (no duplicates)
- `chk_qty_on_hand`: on-hand quantity can never go negative

---

# Key Relationships Summary

| Child Table | Parent Table | On Delete |
|---|---|---|
| purchase_orders | suppliers | RESTRICT |
| purchase_orders | employees | SET NULL |
| purchase_order_lines | purchase_orders | CASCADE |
| purchase_order_lines | products | RESTRICT |
| receiving_transactions | purchase_order_lines | RESTRICT |
| receiving_transactions | warehouses | RESTRICT |
| inventory_balances | warehouses | RESTRICT |
| inventory_balances | products | RESTRICT |
| employees | departments | RESTRICT |
| employees | warehouses | SET NULL |

`RESTRICT` is the default across most relationships intentionally: master data (suppliers, products, warehouses) shouldn't be deletable while transactional history still references it. `CASCADE` is used only for `purchase_order_lines`, since a line item has no meaning without its parent PO.