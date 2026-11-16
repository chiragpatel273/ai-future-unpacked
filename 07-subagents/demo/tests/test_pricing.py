import unittest
from datetime import date

from shop.cart import Cart, Item
from shop.coupons import check_coupon, find_coupon
from shop.pricing import price_breakdown
from shop.rules import discount_for


class CouponTests(unittest.TestCase):
    def test_unknown_coupon(self):
        self.assertIsNone(find_coupon("NOPE"))

    def test_expired_coupon(self):
        self.assertIsNone(find_coupon("SUMMER24", today=date(2026, 11, 1)))

    def test_code_is_not_case_sensitive(self):
        self.assertIsNotNone(find_coupon(" save10 "))

    def test_minimum_cart(self):
        self.assertIn("at least", check_coupon("SAVE25", 50.0))

    def test_percent_off(self):
        items = [Item("A", "Lamp", 40.0, 1)]
        self.assertEqual(discount_for(find_coupon("SAVE10"), items), 4.0)

    def test_amount_off_never_more_than_cart(self):
        items = [Item("A", "Pen", 3.0, 1)]
        self.assertEqual(discount_for(find_coupon("FIVEOFF"), items), 3.0)


class CartTests(unittest.TestCase):
    def test_add_same_item_twice(self):
        cart = Cart()
        cart.add(Item("A", "Lamp", 40.0, 1))
        cart.add(Item("A", "Lamp", 40.0, 2))
        self.assertEqual(cart.items[0].qty, 3)

    def test_subtotal(self):
        cart = Cart([Item("A", "Lamp", 40.0, 1), Item("B", "Mug", 12.5, 2)])
        self.assertEqual(cart.subtotal(), 65.0)

    def test_total_with_coupon(self):
        cart = Cart([Item("A", "Lamp", 40.0, 1)], coupon="SAVE10")
        b = price_breakdown(cart)
        self.assertEqual(b.discount, 4.0)


if __name__ == "__main__":
    unittest.main()
