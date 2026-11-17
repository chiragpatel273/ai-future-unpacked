# Quickstart

This page builds a cart with two products, applies a coupon and prints the total. Copy each step into a file called `shop.py` and run it.

## 1. Create a cart

`cart = Cart(currency="USD")` makes an empty cart. The full list of options is on the [Cart API](../api/cart.md) page.

## 2. Add products

`cart.add(Product("mug", 12.00), qty=3)` adds three mugs. Products are explained in [Products](../api/products.md).

## 3. Apply a coupon

`cart.apply_coupon("SAVE10")` takes 10% off. Rules for stacking and sale items are in the [Coupons guide](../guides/coupons.md).

## 4. Show the total

`print(cart.total())` prints the total with shipping and tax. To change the tax region or the free-shipping limit, edit the settings described in [Configure tinycart](./configure.md).

## Example

```python
from tinycart import Cart, Product, Settings

# Quickstart: a complete example you can run
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

> Note: the numbers above use the default settings. If you changed any setting, your quickstart results will differ. Run the example again after each change to see what moved, and compare it with the table on this page.

## See also

- [Shipping](../guides/shipping.md)
- [Taxes](../guides/taxes.md)
- ![The cart after step 4](../images/cart-flow.png)
