"""The shopping cart."""
from dataclasses import dataclass, field

MAX_QTY = 20  # per item


@dataclass
class Item:
    sku: str
    name: str
    price: float          # price for one unit
    qty: int = 1
    on_sale: bool = False  # already discounted in the catalog

    def line_total(self):
        return round(self.price * self.qty, 2)


@dataclass
class Cart:
    items: list = field(default_factory=list)
    coupon: str = ""

    def add(self, item):
        if item.qty < 1:
            raise ValueError("Quantity must be at least 1.")
        for existing in self.items:
            if existing.sku == item.sku:
                existing.qty = min(existing.qty + item.qty, MAX_QTY)
                return
        item.qty = min(item.qty, MAX_QTY)
        self.items.append(item)

    def set_qty(self, sku, qty):
        if qty <= 0:
            return self.remove(sku)
        for item in self.items:
            if item.sku == sku:
                item.qty = min(qty, MAX_QTY)
                return
        raise KeyError(sku)

    def remove(self, sku):
        self.items = [i for i in self.items if i.sku != sku]

    def clear(self):
        self.items = []
        self.coupon = ""

    def count(self):
        return sum(i.qty for i in self.items)

    def subtotal(self):
        return round(sum(i.line_total() for i in self.items), 2)

    def apply_coupon(self, code):
        self.coupon = code

    def total(self, country="US"):
        from shop.pricing import cart_total
        return cart_total(self, country)
