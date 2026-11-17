# Shipping

Shipping is added after discounts and before tax. tinycart has flat-rate shipping built in and lets you plug in your own rates.

## Free shipping

Orders of `free_shipping_over` or more ship free. The default limit is 50.00, so an order of exactly 50.00 ships free. Change the limit in [Configuration](../getting-started/configuration.md).

## Rates by country

Each country can have its own flat rate. The full table of default rates is on the [Shipping rates](../api/shipping-rates.md) page.

## Custom rates

To call a carrier for live rates, pass a function to `Cart(shipping=...)`. The function gets the cart and returns a price. See the [Cart API](../api/cart.md).

## Example

```python
from tinycart import Cart, Product, Settings

# Shipping: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your shipping results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Taxes](taxes.md)
- ![Where shipping is added](../images/cart-flow.png)
