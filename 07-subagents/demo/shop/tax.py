"""Simplified sales tax / VAT by country, as a fraction of the amount."""

TAX_RATES = {"US": 0.07, "CA": 0.13, "GB": 0.20, "DE": 0.19, "IN": 0.18, "AU": 0.10}


def tax_for(amount, country="US"):
    """Tax on an amount (after discounts, before shipping)."""
    rate = TAX_RATES.get(country, 0.0)
    return round(amount * rate, 2)


def price_with_tax(amount, country="US"):
    return round(amount + tax_for(amount, country), 2)
