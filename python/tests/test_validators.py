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
    check_receiving_quantity_mismatch,
    check_receiving_negative_quantities,
    check_receiving_before_order,
    check_receiving_unknown_warehouse,
    check_receiving_duplicate_event,
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


# ---------------------------------------------------------------------------
# Receiving event validators
# ---------------------------------------------------------------------------

def _receiving_row(**overrides):
    row = {
        "po_number": "PO-2026-1000", "sku": "PROD-SKU-1001", "event_number": 1,
        "order_date": "2026-06-01", "received_date": "2026-06-10",
        "warehouse_code": "WH-ORL-01", "quantity_received": 100,
        "quantity_accepted": 95, "quantity_damaged": 5, "quantity_rejected": 0,
    }
    row.update(overrides)
    return row


def test_receiving_quantity_mismatch_flagged():
    df = pd.DataFrame([_receiving_row(quantity_received=110)])
    assert len(check_receiving_quantity_mismatch(df)) == 1


def test_receiving_quantity_breakdown_clean_passes():
    df = pd.DataFrame([_receiving_row()])
    assert len(check_receiving_quantity_mismatch(df)) == 0


def test_receiving_negative_damaged_flagged():
    df = pd.DataFrame([_receiving_row(quantity_damaged=-3, quantity_accepted=98, quantity_received=95)])
    assert len(check_receiving_negative_quantities(df)) == 1


def test_receiving_before_order_flagged():
    df = pd.DataFrame([_receiving_row(received_date="2026-05-20")])  # before 2026-06-01 order_date
    assert len(check_receiving_before_order(df)) == 1


def test_receiving_unknown_warehouse_flagged():
    df = pd.DataFrame([_receiving_row(warehouse_code="WH-XXX-99")])
    assert len(check_receiving_unknown_warehouse(df)) == 1


def test_receiving_known_warehouse_passes():
    df = pd.DataFrame([_receiving_row()])
    assert len(check_receiving_unknown_warehouse(df)) == 0


def test_receiving_duplicate_event_flagged():
    df = pd.DataFrame([_receiving_row(), _receiving_row()])
    assert len(check_receiving_duplicate_event(df)) == 2


def test_receiving_different_event_numbers_not_duplicate():
    df = pd.DataFrame([_receiving_row(event_number=1), _receiving_row(event_number=2)])
    assert len(check_receiving_duplicate_event(df)) == 0