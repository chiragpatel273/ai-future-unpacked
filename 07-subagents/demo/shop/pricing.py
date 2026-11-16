"""Works out what a customer pays.

    subtotal  - coupon discount  = after_discount
    after_discount + shipping + tax = total
"""
from dataclasses import dataclass

from shop.coupons import check_coupon, find_coupon
from shop.rules import discount_for
from shop.shipping import shipping_cost
from shop.tax import tax_for


@dataclass
class Breakdown:
    subtotal: float
    discount: float
    shipping: float
    tax: float
    total: float
    coupon_message: str = ""


def price_breakdown(cart, country="US"):
    """Every line of the receipt, so the checkout page can show it."""
    subtotal = cart.subtotal()
    discount = 0.0
    message = ""
    if cart.coupon:
        message = check_coupon(cart.coupon, subtotal)
        if not message:
            coupon = find_coupon(cart.coupon)
            discount = discount_for(coupon, cart.items)
    after_discount = max(subtotal - discount, 0.0)
    shipping = shipping_cost(after_discount, country)
    tax = tax_for(after_discount, country)
    total = round(after_discount + shipping + tax, 2)
    return Breakdown(subtotal, round(discount, 2), shipping, tax, total, message)


def cart_total(cart, country="US"):
    """Subtotal - coupon discount + shipping + tax."""
    return price_breakdown(cart, country).total


def format_receipt(b):
    lines = [f"Subtotal   ${b.subtotal:8.2f}"]
    if b.discount:
        lines.append(f"Discount  -${b.discount:8.2f}")
    if b.coupon_message:
        lines.append(f"Coupon: {b.coupon_message}")
    lines += [f"Shipping   ${b.shipping:8.2f}", f"Tax        ${b.tax:8.2f}", f"Total      ${b.total:8.2f}"]
    return "\n".join(lines)
