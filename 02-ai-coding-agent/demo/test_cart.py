import unittest
from cart import cart_total


class TestCart(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cart_total([(10.0, 2), (5.0, 1)]), 25.0)

    def test_ten_percent_discount(self):
        self.assertEqual(cart_total([(10.0, 2), (5.0, 1)], 0.10), 22.5)


if __name__ == "__main__":
    unittest.main()
