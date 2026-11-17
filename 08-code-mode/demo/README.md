# tinycart documentation

tinycart is a small shopping-cart library for Python web shops. It keeps the cart, works out prices, applies coupons, adds shipping and tax, and sends the order email. These pages explain how to install it, how each part works, and what every function does.

## Start here

New to tinycart? Read [Install](getting-started/install.md) first, then follow the [Quickstart](getting-started/quickstart.md). It builds a working cart in about ten minutes. When you are ready to change the defaults, see [Configuration](getting-started/configuration.md).

## Guides

The guides explain one topic each, with examples: [Coupons](guides/coupons.md), [Shipping](guides/shipping.md), [Taxes](guides/taxes.md), [Order emails](guides/emails.md), [Refunds](guides/refunds.md) and [Inventory](guides/inventory.md).

## API reference

Every public function is listed in the API pages: [Cart](api/cart.md), [Pricing](api/pricing.md), [Orders](api/orders.md), [Products](api/products.md) and [Webhooks](api/webhooks.md). Errors are listed in [Error codes](reference/errors.md).

## Upgrading

Moving from version 1? Read the [Migration guide](reference/migration.md) and the [Changelog](reference/changelog.md). Questions that come up often are answered in the [FAQ](reference/faq.md).

## Help

Found a bug? Open an issue on [GitHub](https://github.com/example/tinycart/issues). You can also write to [support](mailto:help@example.com).

## Example

```python
from tinycart import Cart, Product, Settings

# tinycart documentation: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your tinycart documentation results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Glossary](reference/glossary.md)
- ![How a cart becomes an order](images/cart-flow.png)
