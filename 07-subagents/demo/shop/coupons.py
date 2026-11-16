"""Coupon codes.

A coupon has a rule (a function name in shop/rules.py), a value for that rule,
an optional expiry date, an optional minimum cart value and an optional limit
on how many times it can be used in total.
"""
from datetime import date

COUPONS = {
    "SAVE10":   {"rule": "percent_off", "value": 10, "expires": date(2027, 1, 31), "min_cart": 0,  "max_uses": None},
    "SAVE25":   {"rule": "percent_off", "value": 25, "expires": date(2026, 12, 31), "min_cart": 80, "max_uses": 500},
    "FIVEOFF":  {"rule": "amount_off",  "value": 5,  "expires": date(2027, 6, 30), "min_cart": 20, "max_uses": None},
    "WELCOME":  {"rule": "percent_off", "value": 15, "expires": None,              "min_cart": 0,  "max_uses": None},
    "SUMMER24": {"rule": "percent_off", "value": 20, "expires": date(2024, 8, 31), "min_cart": 0,  "max_uses": 1000},
}

USES = {}  # code -> how many times it has been used (a real shop keeps this in a database)


def normalize(code):
    """Codes are not case-sensitive and may have spaces around them."""
    return (code or "").strip().upper()


def find_coupon(code, today=None):
    """Return the coupon for a code, or None if it is unknown or expired."""
    code = normalize(code)
    if not code:
        return None
    coupon = COUPONS.get(code)
    if coupon is None:
        return None
    today = today or date.today()
    if coupon["expires"] and coupon["expires"] < today:
        return None
    return coupon


def check_coupon(code, cart_value, today=None):
    """Explain why a code can't be used, or return "" if it can."""
    coupon = find_coupon(code, today)
    if coupon is None:
        return "This code is unknown or has expired."
    if cart_value < coupon["min_cart"]:
        return f"This code needs a cart of at least ${coupon['min_cart']}."
    if coupon["max_uses"] is not None and USES.get(normalize(code), 0) >= coupon["max_uses"]:
        return "This code has been used too many times."
    return ""


def record_use(code):
    code = normalize(code)
    USES[code] = USES.get(code, 0) + 1
