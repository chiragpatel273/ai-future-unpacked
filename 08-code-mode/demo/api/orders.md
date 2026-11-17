# Orders API

An order is a cart that was paid for. It keeps a copy of the prices at the time of payment.

## Order.from_cart(cart)

Creates an order from a cart. The cart is emptied. See [Cart API](cart.md).

## Statuses

`paid`, `shipped`, `refunded`, `partly_refunded`. Refund rules are in [Refunds](refunds.md).

## Receipt

`order.receipt()` returns the values used by the email template: items, line totals, discount, shipping, tax and total. See [Order emails](../guides/emails.md).

## Webhooks

Status changes can call your server. See [Webhooks](webhooks.md).

## Example

```python
from tinycart import Cart, Product, Settings

# Orders API: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your orders results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Products](products.md)
- [Error codes](../reference/errors.md)
