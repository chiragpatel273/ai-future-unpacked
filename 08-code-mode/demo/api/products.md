# Products API

A `Product` has a name, a price, an optional sale price and a stock number.

## Product(name, price, sale_price=None, stock=None)

`stock=None` means unlimited. Stock is explained in [Inventory](../guides/inventory.md).

## Sale prices

When `sale_price` is set, the item counts as on sale. Percent coupons skip sale items; see [Coupons](../guides/coupons.md).

## Loading products

`load_products(path)` reads products from a CSV file with the columns name, price, sale_price, stock.

## Example

```python
from tinycart import Cart, Product, Settings

# Products API: a complete example you can run
settings = Settings(currency="USD", tax_region="US-CA", free_shipping_over=50.00)
cart = Cart(currency="USD", settings=settings)
cart.add(Product("mug", 12.00, stock=40), qty=3)
cart.add(Product("tea", 8.50, sale_price=6.00, stock=12), qty=2)
cart.apply_coupon("SAVE10")

for line in cart.lines():
    print(f"{line.qty} x {line.product.name:<6} {line.total:>8.2f}")
print(f"subtotal {cart.subtotal():>8.2f}")
print(f"discount {cart.discount():>8.2f}")
print(f"shipping {cart.shipping():>8.2f}")
print(f"tax      {cart.tax():>8.2f}")
print(f"total    {cart.total():>8.2f}")
```

Output:

```text
3 x mug       36.00
2 x tea       12.00
subtotal    48.00
discount    -3.60
shipping     5.00
tax          4.24
total       53.64
```

> Note: the numbers above use the default settings. If you changed any setting, your products results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Cart API](cart.md)
- [Pricing](pricing.md)
