def percent_off(value, items):
    """Take value% off the cart."""
    # Sale items are already discounted, so coupons don't stack on them.
    if any(i.on_sale for i in items):
        return 0.0
    eligible = sum(i.price * i.qty for i in items)
    return round(eligible * value / 100, 2)


def amount_off(value, items):
    """Take a fixed amount off, but never more than the cart is worth."""
    total = sum(i.price * i.qty for i in items)
    return min(value, total)


RULES = {"percent_off": percent_off, "amount_off": amount_off}


def discount_for(coupon, items):
    return RULES[coupon["rule"]](coupon["value"], items)
