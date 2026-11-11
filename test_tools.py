
from tools import lookup_order, calculate


def test_valid_order():
    result = lookup_order("ORD-1042")
    assert result["status"] == "Shipped"
    assert result["total_gbp"] == 2088.00


def test_missing_order():
    result = lookup_order("ORD-9999")
    assert "error" in result


def test_invalid_order():
    result = lookup_order("ABC")
    assert "error" in result


def test_calculator():
    assert calculate("157 * 246") == "38622"


test_valid_order()
test_missing_order()
test_invalid_order()
test_calculator()

print("All tests passed!")
