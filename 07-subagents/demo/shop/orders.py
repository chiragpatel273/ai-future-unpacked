import itertools
from datetime import datetime

from shop.emails import order_confirmation

_ids = itertools.count(1001)


class Order:
    def __init__(self, cart, email, country="US"):
        self.id = next(_ids)
        self.items = list(cart.items)
        self.email = email
        self.country = country
        self.total = cart.total()
        self.status = "placed"
        self.created = datetime.now()

    def cancel(self):
        if self.status == "shipped":
            raise ValueError("Shipped orders can't be cancelled.")
        self.status = "cancelled"

    def ship(self):
        if self.status != "placed":
            raise ValueError(f"Can't ship an order that is {self.status}.")
        self.status = "shipped"


def place_order(cart, email, country="US"):
    if not cart.items:
        raise ValueError("The cart is empty.")
    order = Order(cart, email, country)
    order_confirmation(order)
    return order
