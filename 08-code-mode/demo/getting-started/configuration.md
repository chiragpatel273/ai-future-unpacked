# Configuration

tinycart reads its settings from a `Settings` object. Every setting has a default, so you only set the ones you want to change.

## Currency and region

`currency` sets the money format and `tax_region` picks the tax table. See [Taxes](../guides/taxes.md) for the regions we support.

## Shipping

`free_shipping_over` is the order total from which shipping is free. The default is 50.00. How the limit is checked is explained in [Shipping](../guides/shipping.md).

## Emails

`email_from` and `email_template` control the order email. See [Order emails](../guides/emails.md).

## Stock

`reserve_stock` holds items for 15 minutes while the customer pays. See [Inventory](../guides/inventory.md).

## Example

```python
from tinycart import Cart, Product, Settings

# Configuration: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your configuration results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Cart API](../api/cart.md#settings)
- [Quickstart](quickstart.md)
