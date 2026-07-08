# Indexing Strategy

## Purpose

This document explains why each non-default index in `sql/schema/03_indexes.sql` exists. PostgreSQL automatically creates indexes for every PRIMARY KEY and UNIQUE constraint, so those aren't repeated here — this covers indexes added deliberately for query performance.

---

# Design Objectives

- Index foreign key columns that are joined on frequently (Postgres does NOT auto-index FK columns)
- Index columns used in WHERE filters on high-volume analytical queries
- Use a composite index where two columns are consistently queried together

---

# Master Data Indexes

| Index | Column(s) | Reason |
|---|---|---|
| `idx_products_sku` | products(sku) | SKU is the natural lookup key during ETL ingestion and validation, even though `product_id` is the PK |
| `idx_warehouses_city` | warehouses(location_city) | Supports geographic/regional reporting filters |

---

# Transactional Indexes

| Index | Column(s) | Reason |
|---|---|---|
| `idx_po_supplier_id` | purchase_orders(supplier_id) | FK join target for supplier scorecarding queries |
| `idx_po_order_date` | purchase_orders(order_date) | Time-series and date-range filtering on POs |
| `idx_pol_po_id` | purchase_order_lines(po_id) | FK join back to parent PO header |
| `idx_pol_product_id` | purchase_order_lines(product_id) | Supports product-velocity/demand queries |
| `idx_employees_department` | employees(department_id) | FK join target |
| `idx_employees_warehouse` | employees(warehouse_id) | FK join target |
| `idx_departments_type` | departments(department_type) | Filtering employees/departments by type |

---

# Composite Indexes

| Index | Column(s) | Reason |
|---|---|---|
| `idx_balances_warehouse_product` | inventory_balances(warehouse_id, product_id) | This pair is queried together for nearly every real-time stock lookup ("how much of product X do we have at warehouse Y"). A composite index here is far more effective than two single-column indexes, since Postgres can satisfy the whole WHERE clause from one index instead of intersecting two. |

---

# What's Intentionally Not Indexed

- `receiving_transactions` has no additional indexes beyond its FK-backed ones inherited from constraints — it's a smaller, append-mostly table and doesn't yet have a known heavy query pattern. Revisit once ETL/reporting queries against it exist.
- Every index here trades a small write-time cost (each INSERT/UPDATE has to maintain the index) for read-time speed. Since this is an OLTP-shaped schema feeding an analytical layer, that trade is worth it, but it's worth stating explicitly rather than indexing everything by default.