# Cart API

The `Cart` class holds the items a customer wants to buy and works out the total.

## Cart(currency, settings=None, shipping=None)

Creates an empty cart. `settings` is a `Settings` object (see [Configuration](../getting-started/configuration.md)). `shipping` is an optional rate function (see [Shipping](../guides/shipping.md)).

## add(product, qty=1)

Adds a product. Raises `OUT_OF_STOCK` when stock is too low. Products are described in [Products](products.md).

## apply_coupon(code)

Applies a coupon. See [Coupons](../guides/coupons.md).

## total()

Returns the total after discounts, shipping and tax. The order of the steps is shown in [Pricing](pricing.md#steps).

## Settings

All settings and their defaults are in [Configuration](../getting-started/configuration.md).

## Example

```python
from tinycart import Cart, Product, Settings

# Cart API: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your cart results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Orders](orders.md)
- ![Cart flow](../images/cart-flow.png)
