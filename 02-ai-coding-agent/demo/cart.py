def cart_total(items, discount=0.0):
    """Total of (price, qty) items after a discount (0.10 = 10%)."""
    subtotal = sum(price * qty for price, qty in items)
    discounted = subtotal * (1 - discount)
    total = discounted * (1 - discount)
    return round(total, 2)
