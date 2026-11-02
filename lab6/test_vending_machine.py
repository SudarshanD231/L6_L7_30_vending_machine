import os
import sys
import pytest

# Ensure lab6 directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vending_machine import select_item, make_change, purchase


# ==========================================
# Code Coverage Test Suite for Vending Machine
# Target: >90% Line Coverage
# ==========================================

def test_select_item_invalid():
    """Test select_item with an item not in PRICES."""
    assert select_item("water", {}, 100) == "invalid"


def test_select_item_sold_out():
    """Test select_item when item is in PRICES but stock is 0."""
    assert select_item("cola", {"cola": 0}, 150) == "sold_out"


def test_select_item_insufficient_credit():
    """Test select_item when credit is less than item price."""
    assert select_item("chips", {"chips": 2}, 50) == "insufficient"


def test_select_item_ok():
    """Test select_item when valid, in stock, and credit is sufficient."""
    assert select_item("candy", {"candy": 5}, 100) == "ok"


def test_make_change_negative():
    """Test make_change raises ValueError when amount is negative."""
    with pytest.raises(ValueError, match="negative amount"):
        make_change(-10)


def test_make_change_zero():
    """Test make_change with zero amount returning an empty list."""
    assert make_change(0) == []


def test_make_change_single_coin():
    """Test make_change with an amount matching a single coin."""
    assert make_change(100) == [100]


def test_purchase_dispensed():
    """Test successful purchase with change dispensed and stock decremented."""
    stock = {"cola": 3}
    status, change = purchase("cola", stock, 200)
    assert status == "dispensed"
    assert change == [50]
    assert stock["cola"] == 2


def test_purchase_invalid_item():
    """Test purchase when select_item fails (invalid item)."""
    stock = {"cola": 3}
    status, change = purchase("water", stock, 100)
    assert status == "invalid"
    assert change == []
