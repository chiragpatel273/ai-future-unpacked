# Pricing API

Pricing turns a cart into money: subtotal, discounts, shipping, tax, total.

## Steps

1. subtotal of all lines, 2. discounts, 3. shipping, 4. tax. Each step is a function you can call on its own for testing.

## Discounts

`percent_off(cart, percent)` and `amount_off(cart, amount)`. Coupons call these; see [Coupons](../guides/coupons.md).

## Tax

`tax_for(cart, region)` uses the tables described in [Taxes](../guides/taxes.md).

## Rounding

All amounts are rounded to two decimals at the end of each step, half up.

## Example

```python
from tinycart import Cart, Product, Settings

# Pricing API: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your pricing results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Cart API](cart.md)
- [Glossary](../reference/glossary.md)
