from shop.cart import Item

# The catalog. on_sale=True means the price is already reduced.
CATALOG = [
    Item("SKU-101", "Desk Lamp", 18.99, on_sale=False),
    Item("SKU-102", "Notebook", 23.99, on_sale=False),
    Item("SKU-103", "Pen Set", 5.99, on_sale=False),
    Item("SKU-104", "Coffee Mug", 5.99, on_sale=False),
    Item("SKU-105", "Backpack", 3.99, on_sale=False),
    Item("SKU-106", "Water Bottle", 11.99, on_sale=True),
    Item("SKU-107", "Headphones", 23.99, on_sale=False),
    Item("SKU-108", "Phone Case", 11.99, on_sale=True),
    Item("SKU-109", "USB Cable", 23.99, on_sale=True),
    Item("SKU-110", "Mouse Pad", 48.99, on_sale=True),
    Item("SKU-111", "Keyboard", 11.99, on_sale=False),
    Item("SKU-112", "Monitor Stand", 48.99, on_sale=False),
    Item("SKU-113", "Plant Pot", 48.99, on_sale=False),
    Item("SKU-114", "Wall Clock", 3.99, on_sale=False),
    Item("SKU-115", "Throw Pillow", 3.99, on_sale=False),
    Item("SKU-116", "Candle", 7.99, on_sale=False),
    Item("SKU-117", "Tea Sampler", 7.99, on_sale=False),
    Item("SKU-118", "Sticky Notes", 48.99, on_sale=False),
    Item("SKU-119", "Desk Organizer", 58.99, on_sale=True),
    Item("SKU-120", "Laptop Sleeve", 48.99, on_sale=False),
    Item("SKU-121", "Bluetooth Speaker", 11.99, on_sale=False),
    Item("SKU-122", "Webcam Cover", 34.99, on_sale=False),
    Item("SKU-123", "Cable Clips", 48.99, on_sale=True),
    Item("SKU-124", "Coaster Set", 11.99, on_sale=False),
]


def by_sku(sku):
    for item in CATALOG:
        if item.sku == sku:
            return Item(item.sku, item.name, item.price, 1, item.on_sale)
    raise KeyError(sku)
