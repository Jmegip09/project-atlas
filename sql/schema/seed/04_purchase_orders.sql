-- Headers
INSERT INTO purchase_orders (po_number, supplier_id, order_date, expected_delivery_date, po_status) VALUES
('PO-2026-0001', 1, '2026-06-01', '2026-06-06', 'Fully Received'),
('PO-2026-0002', 2, '2026-06-15', '2026-06-27', 'Partially Received'),
('PO-2026-0003', 3, '2026-07-01', '2026-07-08', 'Open');

-- Line Items
INSERT INTO purchase_order_lines (po_id, product_id, quantity_ordered, quantity_received, unit_cost) VALUES
(1, 1, 200, 200, 45.00),
(1, 2, 50, 50, 85.50),
(2, 3, 10, 4, 1200.00),
(2, 4, 25, 25, 350.00),
(3, 5, 150, 0, 18.75);