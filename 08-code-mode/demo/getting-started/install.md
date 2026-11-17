# Install

tinycart needs Python 3.10 or newer. It has no other required packages. Install it with pip into the same environment as your web shop.

## With pip

Run `pip install tinycart`. To check the install, run `python -c "import tinycart; print(tinycart.__version__)"`. You should see a version number such as 2.4.0.

## Optional extras

For order emails with HTML templates, install `tinycart[email]`. For Stripe webhooks, install `tinycart[stripe]`. Each extra is described in its guide: [Order emails](../guides/emails.md) and [Webhooks](../api/webhooks.md).

## Next step

Continue with the [Quickstart](quickstart.md). If pip shows an error, look it up in [Error codes](../reference/errors.md) or the [FAQ](../reference/faq.md).

## Example

```python
from tinycart import Cart, Product, Settings

# Install: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your install results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Configuration](configuration.md)
- [Python downloads](https://www.python.org/downloads/)
