# Coupons

A coupon changes the price of a cart. tinycart supports percent coupons, fixed-amount coupons and free-shipping coupons.

## Percent coupons

`SAVE10` takes 10% off every item that is not on sale. Items on sale keep their sale price. The maths is described in [Pricing](../api/pricing.md#discounts).

## Fixed-amount coupons

A fixed coupon such as `TAKE5` takes 5.00 off the whole cart, never below zero. Every discount type has its own page in the [Discounts API](../api/discounts.md).

## Limits

One coupon per cart by default. To allow stacking, set `max_coupons` in [Configuration](../getting-started/configuration.md). A coupon that fails returns an error from [Error codes](../reference/errors.md).

## Example

```python
from tinycart import Cart, Product, Settings

# Coupons: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your coupons results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Refunds](refunds.md) (what happens to a coupon when an order is refunded)
- [Glossary](../reference/glossary.md)
