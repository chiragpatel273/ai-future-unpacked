"""Shipping: flat rates by country, free over a threshold, optional express."""

RATES = {"US": 4.99, "CA": 7.99, "GB": 8.49, "DE": 8.49, "IN": 3.49, "AU": 11.99}
FREE_OVER = {"US": 50, "CA": 75, "GB": 60, "DE": 60, "IN": 40, "AU": 100}
EXPRESS_EXTRA = 9.99
DEFAULT_RATE = 14.99  # countries we don't list


def shipping_cost(amount, country="US", express=False):
    if amount <= 0:
        return 0.0
    rate = RATES.get(country, DEFAULT_RATE)
    free_over = FREE_OVER.get(country)
    if free_over is not None and amount > free_over:
        rate = 0.0
    return round(rate + (EXPRESS_EXTRA if express else 0.0), 2)


def delivery_days(country="US", express=False):
    base = {"US": 4, "CA": 6, "GB": 7, "DE": 7, "IN": 9, "AU": 10}.get(country, 14)
    return max(1, base // 2) if express else base


def ships_to(country):
    return country in RATES
