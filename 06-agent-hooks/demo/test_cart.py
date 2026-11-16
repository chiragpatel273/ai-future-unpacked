import unittest
from cart import cart_total

ITEMS = [(10.0, 2), (5.0, 1)]          # subtotal 25.00

class CartTest(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cart_total(ITEMS), 25.0)

    def test_ten_percent(self):
        self.assertEqual(cart_total(ITEMS, 0.10), 22.5)

    def test_discount_capped_at_50_percent(self):
        self.assertEqual(cart_total(ITEMS, 0.80), 12.5)

    def test_rejects_negative_discount(self):
        with self.assertRaises(ValueError):
            cart_total(ITEMS, -0.2)

if __name__ == "__main__":
    unittest.main()
