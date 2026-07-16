"""
Reliability profiles used by generate_receiving_raw.py to simulate
realistic, supplier-specific receiving behavior instead of pure randomness.

Values are loosely anchored to what sql/queries/02_supplier_delivery_performance.sql
already shows about planned lead times, so the receiving story and the PO
story agree with each other: Global Core is the most reliable supplier in
both, Beacon Packaging is the least reliable in both.

on_time_probability        chance a receipt event lands on/before the PO's
                            expected_delivery_date
partial_receipt_probability chance a line ships across 2 events instead of 1
damage_probability          fraction of a shipment's units damaged in transit
rejection_probability       fraction rejected outright (wrong item, failed QC)
"""

SUPPLIER_PROFILES = {
    "Global Core Manufacturing": {
        "on_time_probability": 0.88,
        "partial_receipt_probability": 0.10,
        "damage_probability": 0.01,
        "rejection_probability": 0.01,
    },
    "Apex Logistics Group": {
        "on_time_probability": 0.75,
        "partial_receipt_probability": 0.18,
        "damage_probability": 0.02,
        "rejection_probability": 0.01,
    },
    "Titan Industrial Supply": {
        "on_time_probability": 0.55,
        "partial_receipt_probability": 0.30,
        "damage_probability": 0.04,
        "rejection_probability": 0.02,
    },
    "Beacon Packaging Corp": {
        "on_time_probability": 0.35,
        "partial_receipt_probability": 0.40,
        "damage_probability": 0.07,
        "rejection_probability": 0.04,
    },
}

DEFAULT_SUPPLIER_PROFILE = {
    "on_time_probability": 0.65,
    "partial_receipt_probability": 0.20,
    "damage_probability": 0.03,
    "rejection_probability": 0.02,
}

# high_volume warehouses get a wider, noisier inspection-delay window --
# more dock traffic, more variance in how fast a receipt gets logged
WAREHOUSE_PROFILES = {
    "WH-ORL-01": {"inspection_delay_hours": (2, 8), "high_volume": True},
    "WH-MIA-02": {"inspection_delay_hours": (4, 24), "high_volume": True},
    "WH-TPA-03": {"inspection_delay_hours": (1, 4), "high_volume": False},
}

DEFAULT_WAREHOUSE_PROFILE = {"inspection_delay_hours": (2, 12), "high_volume": False}