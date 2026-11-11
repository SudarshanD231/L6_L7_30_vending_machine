"""
Property-Based Fuzz Testing Suite for Vending Machine Application
Using the Hypothesis Fuzzing Library (Lab 7)

Targets:
1. select_item(item, stock, credit)
2. make_change(amount)
3. purchase(item, stock, credit)
"""

import os
import sys
import pytest
from hypothesis import given, strategies as st, settings

# Ensure the lab7 directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processor import select_item, make_change, purchase, PRICES, COINS


# =====================================================================
# Strategy Definitions for Fuzzing
# =====================================================================

# Basic types & malformed data strategies
any_item_strategy = st.one_of(
    st.sampled_from(["cola", "chips", "candy"]),  # Valid items
    st.text(max_size=20),                          # Random unicode strings
    st.integers(min_value=-1000, max_value=1000),  # Unexpected integers
    st.none(),                                     # None
    st.booleans(),                                 # Booleans
)

any_stock_strategy = st.one_of(
    st.dictionaries(st.text(max_size=10), st.integers(min_value=-50, max_value=50), max_size=5), # General dictionaries
    st.none(),                                     # None (common bug trigger)
    st.text(max_size=10),                          # Malformed string
    st.integers(min_value=-50, max_value=50),      # Malformed integer
    st.lists(st.integers(min_value=-10, max_value=10), max_size=5), # Malformed list
)

any_credit_strategy = st.one_of(
    st.integers(min_value=-1000, max_value=2000),  # Negative, zero, large integers
    st.none(),                                     # None
    st.text(max_size=10),                          # Malformed string
    st.floats(min_value=-1000.0, max_value=2000.0, allow_nan=False, allow_infinity=False), # Floats
    st.booleans(),                                 # Booleans
)

any_amount_strategy = st.one_of(
    st.integers(min_value=-1000, max_value=2000),  # Negative, 0, positive integers
    st.none(),                                     # None
    st.text(max_size=10),                          # Strings
    st.floats(min_value=-1000.0, max_value=2000.0, allow_nan=False, allow_infinity=False), # Floats
    st.booleans(),                                 # Booleans
)

VALID_STATUSES = {"ok", "invalid", "sold_out", "insufficient"}
VALID_PURCHASE_STATUSES = {"dispensed", "invalid", "sold_out", "insufficient", "no_exact_change"}


# =====================================================================
# FUNCTION 1: select_item(item, stock, credit) Fuzz Tests
# =====================================================================

@given(item=any_item_strategy, stock=any_stock_strategy, credit=any_credit_strategy)
@settings(max_examples=100, deadline=1500)
def test_select_item_no_crash(item, stock, credit):
    """
    Fuzz Property: select_item should NEVER crash regardless of input types or values.
    It must safely return one of the contract status strings.
    """
    try:
        result = select_item(item, stock, credit)
    except Exception as exc:
        pytest.fail(f"select_item crashed on input (item={item!r}, stock={stock!r}, credit={credit!r}) with {type(exc).__name__}: {exc}")

    assert result in VALID_STATUSES, f"Unexpected return value: {result!r}"


@given(
    item=st.sampled_from(["cola", "chips", "candy"]),
    stock_count=st.integers(min_value=0, max_value=100),
    credit=st.integers(min_value=0, max_value=1000)
)
@settings(max_examples=100, deadline=1500)
def test_select_item_valid_invariants(item, stock_count, credit):
    """
    Property: For valid domain inputs, select_item must obey vending machine business logic.
    """
    stock = {item: stock_count}
    result = select_item(item, stock, credit)

    if stock_count <= 0:
        assert result == "sold_out"
    elif credit < PRICES[item]:
        assert result == "insufficient"
    else:
        assert result == "ok"


# =====================================================================
# FUNCTION 2: make_change(amount) Fuzz Tests
# =====================================================================

@given(amount=any_amount_strategy)
@settings(max_examples=100, deadline=1500)
def test_make_change_no_crash(amount):
    """
    Fuzz Property: make_change must NEVER crash with unhandled exceptions.
    Invalid or negative inputs must be safely handled (returning None).
    """
    try:
        result = make_change(amount)
    except Exception as exc:
        pytest.fail(f"make_change crashed on input (amount={amount!r}) with {type(exc).__name__}: {exc}")

    assert result is None or isinstance(result, list), f"Unexpected return type: {type(result)}"


@given(amount=st.integers(min_value=0, max_value=10000))
@settings(max_examples=100, deadline=1500)
def test_make_change_valid_properties(amount):
    """
    Property: For non-negative integers, if change is returned:
    1. sum(coins) must equal amount.
    2. All coins must be legal denominations from COINS.
    3. Coins must be returned in descending order.
    """
    coins = make_change(amount)
    if coins is not None:
        assert sum(coins) == amount, f"Sum of coins {coins} does not equal amount {amount}"
        assert all(c in COINS for c in coins), f"Illegal coin denomination in {coins}"
        assert coins == sorted(coins, reverse=True), f"Coins not sorted descending: {coins}"


# =====================================================================
# FUNCTION 3: purchase(item, stock, credit) Fuzz Tests
# =====================================================================

@given(item=any_item_strategy, stock=any_stock_strategy, credit=any_credit_strategy)
@settings(max_examples=100, deadline=1500)
def test_purchase_no_crash(item, stock, credit):
    """
    Fuzz Property: purchase must NEVER crash on arbitrary inputs.
    It must return a tuple (status, change_list).
    """
    try:
        result = purchase(item, stock, credit)
    except Exception as exc:
        pytest.fail(f"purchase crashed on input (item={item!r}, stock={stock!r}, credit={credit!r}) with {type(exc).__name__}: {exc}")

    assert isinstance(result, tuple) and len(result) == 2, f"Expected 2-tuple, got {result!r}"
    status, change = result
    assert status in VALID_PURCHASE_STATUSES, f"Unexpected purchase status: {status!r}"
    assert isinstance(change, list), f"Expected list for change, got {type(change)}"


@given(
    item=st.sampled_from(["cola", "chips", "candy"]),
    stock_count=st.integers(min_value=0, max_value=50),
    credit=st.integers(min_value=0, max_value=500)
)
@settings(max_examples=100, deadline=1500)
def test_purchase_state_integrity(item, stock_count, credit):
    """
    Property: When purchasing with valid domain inputs:
    - If status == 'dispensed', stock must decrement by exactly 1 and change sum == credit - price.
    - If status != 'dispensed', stock must remain unchanged.
    """
    stock = {item: stock_count}
    status, change = purchase(item, stock, credit)

    if status == "dispensed":
        assert stock[item] == stock_count - 1, "Stock did not decrement on dispensed purchase!"
        assert sum(change) == credit - PRICES[item], "Change does not match credit minus price!"
    else:
        assert stock[item] == stock_count, "Stock modified on unfulfilled purchase!"
        assert change == [], f"Expected empty change list on non-dispensed, got {change}"
