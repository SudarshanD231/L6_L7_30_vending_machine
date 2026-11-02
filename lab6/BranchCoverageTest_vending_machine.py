import os
import sys
import pytest

# Ensure lab6 directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vending_machine import select_item, make_change, purchase


# ==============================================================
# Branch Coverage Test Suite for Vending Machine
# Target: 100% Branch Coverage & 100% Line Coverage
# ==============================================================

# --------------------------------------------------------------
# 1. select_item Branch Tests
# --------------------------------------------------------------

def test_select_item_invalid_not_in_prices():
    """Branch: item not in PRICES (True branch)."""
    assert select_item("water", {}, 100) == "invalid"


def test_select_item_sold_out_zero_stock():
    """Branch: item not in PRICES (False), stock.get(item, 0) == 0 (True)."""
    assert select_item("chips", {"chips": 0}, 100) == "sold_out"


def test_select_item_sold_out_missing_from_stock_dict():
    """Branch: item not in PRICES (False), missing key in stock dict -> default 0 (True)."""
    assert select_item("chips", {}, 100) == "sold_out"


def test_select_item_insufficient_credit():
    """Branch: in stock (False), credit < PRICES[item] (True)."""
    assert select_item("cola", {"cola": 5}, 100) == "insufficient"


def test_select_item_exact_credit():
    """Branch: credit < PRICES[item] (False - boundary credit == price)."""
    assert select_item("candy", {"candy": 5}, 75) == "ok"


def test_select_item_excess_credit():
    """Branch: credit < PRICES[item] (False - credit > price)."""
    assert select_item("cola", {"cola": 5}, 200) == "ok"


# --------------------------------------------------------------
# 2. make_change Branch Tests
# --------------------------------------------------------------

def test_make_change_negative_amount():
    """Branch: amount < 0 (True -> raises ValueError)."""
    with pytest.raises(ValueError, match="negative amount"):
        make_change(-1)


def test_make_change_negative_large():
    """Branch: amount < 0 (True -> raises ValueError)."""
    with pytest.raises(ValueError, match="negative amount"):
        make_change(-100)


def test_make_change_zero():
    """Branch: amount < 0 (False), while amount >= coin never entered, amount > 0 (False)."""
    assert make_change(0) == []


def test_make_change_exact_single_coin():
    """Branch: while loop entered for matching coin, bypassed for others, amount > 0 (False)."""
    assert make_change(100) == [100]
    assert make_change(50) == [50]
    assert make_change(25) == [25]
    assert make_change(10) == [10]
    assert make_change(5) == [5]


def test_make_change_multiple_same_coin():
    """Branch: while loop executes multiple times for the same coin."""
    assert make_change(200) == [100, 100]
    assert make_change(20) == [10, 10]


def test_make_change_mixed_coins():
    """Branch: while loop executes for multiple different coin denominations."""
    # 100 + 50 + 25 + 10 + 5 = 190
    assert make_change(190) == [100, 50, 25, 10, 5]


def test_make_change_impossible_small_remainder():
    """Branch: amount > 0 remaining after loop when initial amount cannot be formed (True)."""
    assert make_change(3) is None
    assert make_change(1) is None


def test_make_change_impossible_after_partial_coins():
    """Branch: amount > 0 remaining after loop when some coins used but remainder cannot be formed (True)."""
    # 14 -> 10 + 4 remainder -> None
    assert make_change(14) is None
    # 68 -> 50 + 10 + 5 + 3 remainder -> None
    assert make_change(68) is None


# --------------------------------------------------------------
# 3. purchase Branch Tests
# --------------------------------------------------------------

def test_purchase_status_invalid_item():
    """Branch: status != 'ok' (True - invalid item)."""
    status, change = purchase("unknown_item", {"cola": 2}, 200)
    assert status == "invalid"
    assert change == []


def test_purchase_status_sold_out():
    """Branch: status != 'ok' (True - sold out item)."""
    status, change = purchase("chips", {"chips": 0}, 100)
    assert status == "sold_out"
    assert change == []


def test_purchase_status_insufficient_credit():
    """Branch: status != 'ok' (True - insufficient credit)."""
    status, change = purchase("cola", {"cola": 2}, 100)
    assert status == "insufficient"
    assert change == []


def test_purchase_no_exact_change():
    """Branch: status != 'ok' (False), change is None (True -> return 'no_exact_change', [])."""
    stock = {"candy": 2}
    # candy price = 75; credit = 78; change required = 3 (cannot be made)
    status, change = purchase("candy", stock, 78)
    assert status == "no_exact_change"
    assert change == []
    assert stock["candy"] == 2  # Stock must not be decremented


def test_purchase_success_exact_change():
    """Branch: status != 'ok' (False), change is None (False), change == []."""
    stock = {"chips": 3}
    status, change = purchase("chips", stock, 100)
    assert status == "dispensed"
    assert change == []
    assert stock["chips"] == 2  # Stock decremented by 1


def test_purchase_success_with_change():
    """Branch: status != 'ok' (False), change is None (False), change dispensed with multiple coins."""
    stock = {"cola": 2}
    # cola price = 150; credit = 200; change = [50]
    status, change = purchase("cola", stock, 200)
    assert status == "dispensed"
    assert change == [50]
    assert stock["cola"] == 1  # Stock decremented by 1
