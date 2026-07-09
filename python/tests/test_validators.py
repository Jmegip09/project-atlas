import pandas as pd

from validation.validators import (
    check_duplicate_po_numbers,
    check_missing_supplier,
    check_unknown_supplier,
    check_delivery_before_order,
    check_negative_quantity,
    check_over_received,
    check_unknown_sku,
    check_zero_or_negative_cost,
)


def test_duplicate_po_numbers_flags_both_rows():
    df = pd.DataFrame({
        "po_number": ["PO-1", "PO-1", "PO-2"],
        "supplier_name": ["Apex Logistics Group"] * 3,
    })
    assert len(check_duplicate_po_numbers(df)) == 2


def test_missing_supplier_flags_blank_and_null():
    df = pd.DataFrame({"po_number": ["PO-1", "PO-2"], "supplier_name": ["", None]})
    assert len(check_missing_supplier(df)) == 2


def test_unknown_supplier_flags_unrecognized_name():
    df = pd.DataFrame({"po_number": ["PO-1"], "supplier_name": ["Nonexistent Vendor LLC"]})
    assert len(check_unknown_supplier(df)) == 1


def test_delivery_before_order_flags_bad_dates():
    df = pd.DataFrame({
        "po_number": ["PO-1"],
        "order_date": ["2026-06-01"],
        "expected_delivery_date": ["2026-05-01"],
    })
    assert len(check_delivery_before_order(df)) == 1


def test_delivery_after_order_passes_clean():
    df = pd.DataFrame({
        "po_number": ["PO-1"],
        "order_date": ["2026-06-01"],
        "expected_delivery_date": ["2026-06-10"],
    })
    assert len(check_delivery_before_order(df)) == 0


def test_negative_quantity_flagged():
    df = pd.DataFrame({"po_number": ["PO-1"], "sku": ["PROD-SKU-1001"], "quantity_ordered": [-5]})
    assert len(check_negative_quantity(df)) == 1


def test_over_received_flagged():
    df = pd.DataFrame({
        "po_number": ["PO-1"], "sku": ["PROD-SKU-1001"],
        "quantity_ordered": [10], "quantity_received": [15],
    })
    assert len(check_over_received(df)) == 1


def test_unknown_sku_flagged():
    df = pd.DataFrame({"po_number": ["PO-1"], "sku": ["PROD-SKU-9999"]})
    assert len(check_unknown_sku(df)) == 1


def test_zero_cost_flagged():
    df = pd.DataFrame({"po_number": ["PO-1"], "sku": ["PROD-SKU-1001"], "unit_cost": [0]})
    assert len(check_zero_or_negative_cost(df)) == 1