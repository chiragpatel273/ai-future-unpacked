def cart_total(items, discount=0.0):
    """Total of (price, qty) items after a discount.

    discount is a fraction: 0.10 means 10% off. It must be between 0 and 1,
    otherwise raise ValueError.
    """
    subtotal = sum(price * qty for price, qty in items)
    return round(subtotal * (1 - discount), 2)
