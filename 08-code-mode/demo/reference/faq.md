# FAQ

Answers to the questions we get most often.

## Why is shipping still charged on a 50.00 order?

Orders of exactly the limit ship free from version 2.4.0. Check your version and the limit in [Configuration](../getting-started/configuration.md).

## Why did my coupon not apply to a sale item?

Percent coupons skip sale items by design. See [Coupons](../guides/coupons.md).

## What does the checkout look like?

This picture shows the steps from cart to receipt: ![Checkout steps](../images/checkout-flow.png)

## How do I test emails without sending them?

Use the console backend described in [Order emails](../guides/emails.md#testing).

## Example

```python
from tinycart import Cart, Product, Settings

# FAQ: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your faq results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Glossary](glossary.md)
- [Error codes](errors.md)
