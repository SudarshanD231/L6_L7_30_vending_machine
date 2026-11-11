"""
Vending Machine Application (Buggy Starter - Lab 7)
Preserved for reproducibility and fuzz failure demonstration.
"""

PRICES = {"cola": 150, "chips": 100, "candy": 75}
COINS = [100, 50, 25, 10, 5]


def select_item(item, stock, credit):
    if item not in PRICES:
        return "invalid"
    if stock.get(item, 0) == 0:
        return "sold_out"
    if credit < PRICES[item]:
        return "insufficient"
    return "ok"


def make_change(amount):
    if amount < 0:
        raise ValueError("negative amount")
    coins = []
    for coin in COINS:
        while amount >= coin:
            coins.append(coin)
            amount -= coin
    if amount > 0:
        return None
    return coins


def purchase(item, stock, credit):
    status = select_item(item, stock, credit)
    if status != "ok":
        return status, []
    change = make_change(credit - PRICES[item])
    if change is None:
        return "no_exact_change", []
    stock[item] -= 1
    return "dispensed", change


if __name__ == "__main__":
    print("=" * 60)
    print("       VENDING MACHINE PROCESSOR (BUGGY APPLICATION)")
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
    print(f" -> make_change(85) = {change_coins} (sum = {sum(change_coins) if change_coins else 0})")
    print("=" * 60)
