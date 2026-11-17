# Taxes

Tax is the last step of the total. tinycart ships tax tables for the US, the EU, the UK and India.

## Choosing a region

Set `tax_region` in [Configuration](../getting-started/configuration.md). The region decides the rate and whether prices include tax.

## Prices with tax included

In the EU, UK and India, shop prices usually include tax. tinycart then shows the tax part on the receipt instead of adding it. The receipt is built by [Order emails](emails.md).

## Tax on shipping

Some regions tax shipping and some do not. The rule per region is in [Pricing](../api/pricing.md#tax).

## Example

```python
from tinycart import Cart, Product, Settings

# Taxes: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your taxes results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Shipping](shipping.md)
- [Glossary](../reference/glossary.md)
