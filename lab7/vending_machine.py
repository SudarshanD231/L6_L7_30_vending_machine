"""
Vending Machine Application Module - Lab 7
Re-exports processor functions for backward compatibility.
"""

from processor import (
    PRICES,
    COINS,
    select_item,
    make_change,
    purchase,
)

__all__ = ["PRICES", "COINS", "select_item", "make_change", "purchase"]
