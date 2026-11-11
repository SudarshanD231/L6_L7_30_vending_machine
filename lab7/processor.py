"""
Vending Machine Application (Hardened / Fixed - Lab 7)

Hardened against unexpected, malformed, or malicious inputs
uncovered during property-based fuzz testing with Hypothesis.

Security & Quality Hardening:
1. Input Validation: Strict type checking on item, stock, credit, and amount.
2. Graceful Error Handling: Returns well-defined contract statuses/None instead of crashing.
3. Denial of Service (DoS) Prevention: Replaced O(N) iterative subtraction with O(1) division
   and added practical upper bounds on monetary transactions to prevent memory exhaustion.
4. Transaction Atomicity: State changes (stock decrement) are only executed if payment,
   stock availability, and exact change calculation succeed.
"""

PRICES = {"cola": 150, "chips": 100, "candy": 75}
COINS = [100, 50, 25, 10, 5]

# Upper bound limits to prevent DoS attacks / memory exhaustion
MAX_TRANSACTION_LIMIT = 100_000


def select_item(item, stock, credit):
    """
    Select an item from the vending machine with strict defensive validation.
    
    Parameters:
        item: Any input (expected string key in PRICES)
        stock: Any input (expected dict mapping items to positive integer stock)
        credit: Any input (expected non-negative integer amount of credit)
        
    Returns:
        "invalid"      - If item is not in catalog or unhashable
        "sold_out"     - If stock is missing, not a mapping, or item count <= 0
        "insufficient" - If credit is invalid, negative, out of bounds, or less than item price
        "ok"           - Item available and credit is sufficient
    """
    # 1. Validate item (defend against unhashable types and non-catalog keys)
    try:
        if item not in PRICES:
            return "invalid"
    except TypeError:
        return "invalid"

    # 2. Validate stock mapping (defend against None, primitives, malformed structures)
    if not isinstance(stock, dict):
        return "sold_out"

    item_stock = stock.get(item, 0)
    # Check that stock is a valid integer count (excluding booleans which subclass int)
    if isinstance(item_stock, bool) or not isinstance(item_stock, int) or item_stock <= 0:
        return "sold_out"

    # 3. Validate credit (defend against None, booleans, strings, negative, or overflow values)
    if isinstance(credit, bool) or not isinstance(credit, (int, float)):
        return "insufficient"

    if credit < 0 or credit > MAX_TRANSACTION_LIMIT:
        return "insufficient"

    if credit < PRICES[item]:
        return "insufficient"

    return "ok"


def make_change(amount):
    """
    Calculate minimal coin denominations for a given change amount.
    
    Parameters:
        amount: Any input (expected non-negative integer)
        
    Returns:
        list of coins in descending order, or None if exact change cannot be made.
        Invalid inputs (None, negative, non-numeric, booleans, or overflow) return None safely.
    """
    # Defensive type check: must be a non-negative integer (excluding bool)
    if isinstance(amount, bool) or not isinstance(amount, int):
        return None

    # Bounds check: negative amounts and DoS-inducing huge amounts
    if amount < 0 or amount > MAX_TRANSACTION_LIMIT:
        return None

    if amount == 0:
        return []

    coins = []
    remaining = amount
    # O(1) arithmetic change calculation (prevents Algorithmic DoS from while loops)
    for coin in COINS:
        count = remaining // coin
        if count > 0:
            coins.extend([coin] * count)
            remaining %= coin

    if remaining > 0:
        return None

    return coins


def purchase(item, stock, credit):
    """
    Execute a purchase transaction with atomic state updates.
    
    Parameters:
        item: Any input
        stock: Any input (expected mutable dict)
        credit: Any input
        
    Returns:
        (status, change): Tuple with transaction status and list of change coins.
        Guarantees that stock is only decremented on successful ('dispensed') transactions.
    """
    status = select_item(item, stock, credit)
    if status != "ok":
        return status, []

    # Extra defense: ensure credit is valid integer and stock is mutable dict
    if not isinstance(stock, dict) or isinstance(credit, bool) or not isinstance(credit, int):
        return status, []

    diff = credit - PRICES[item]
    change = make_change(diff)
    if change is None:
        return "no_exact_change", []

    # Atomically verify and decrement stock
    current_stock = stock.get(item, 0)
    if isinstance(current_stock, int) and not isinstance(current_stock, bool) and current_stock > 0:
        stock[item] = current_stock - 1
    else:
        return "sold_out", []

    return "dispensed", change


if __name__ == "__main__":
    print("=" * 60)
    print("       VENDING MACHINE PROCESSOR (HARDENED APPLICATION)")
    print("=" * 60)
    
    initial_stock = {"cola": 5, "chips": 3, "candy": 2}
    print(f"Initial Stock: {initial_stock}")
    print(f"Available Items & Prices: {PRICES}")
    print(f"Coin Denominations: {COINS}\n")

    # Transaction 1: Successful purchase with change
    print("[Transaction 1] Buying 'cola' with 200 credit:")
    sel = select_item("cola", initial_stock, 200)
    print(f" -> select_item('cola', stock, 200) = '{sel}'")
    status, change = purchase("cola", initial_stock, 200)
    print(f" -> purchase('cola', stock, 200) = status: '{status}', change: {change}")
    print(f" -> Stock after purchase: {initial_stock}\n")

    # Transaction 2: Item sold out
    print("[Transaction 2] Buying 'chips' with empty stock:")
    out_of_stock = {"chips": 0}
    sel = select_item("chips", out_of_stock, 100)
    print(f" -> select_item('chips', stock, 100) = '{sel}'")
    status, change = purchase("chips", out_of_stock, 100)
    print(f" -> purchase('chips', stock, 100) = status: '{status}', change: {change}\n")

    # Transaction 3: Insufficient credit
    print("[Transaction 3] Buying 'candy' with 50 credit (price=75):")
    sel = select_item("candy", initial_stock, 50)
    print(f" -> select_item('candy', stock, 50) = '{sel}'")
    status, change = purchase("candy", initial_stock, 50)
    print(f" -> purchase('candy', stock, 50) = status: '{status}', change: {change}\n")

    # Transaction 4: Change calculation
    print("[Transaction 4] Making change for 85:")
    change_coins = make_change(85)
    print(f" -> make_change(85) = {change_coins} (sum = {sum(change_coins) if change_coins else 0})\n")

    # Transaction 5: Edge cases handled safely (Defense against fuzz bugs)
    print("[Transaction 5] Defensive edge cases (fuzz test scenarios):")
    print(" -> make_change(-25) =", make_change(-25), "(graceful None, no crash)")
    print(" -> make_change(None) =", make_change(None), "(graceful None, no crash)")
    print(" -> select_item('cola', None, 200) =", select_item("cola", None, 200), "(graceful 'sold_out')")
    print(" -> select_item('cola', {'cola': 5}, None) =", select_item("cola", {"cola": 5}, None), "(graceful 'insufficient')")
    print(" -> purchase(['invalid_type'], None, None) =", purchase(["invalid_type"], None, None), "(safe tuple, no crash)")
    print("=" * 60)
