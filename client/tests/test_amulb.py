from aplusb import mul
import unittest

class TestMul(unittest.TestCase):
    def test_mul1(self):
        self.assertEqual(mul(2, 3), 6)
        self.assertEqual(mul(0, 0), 0)
        self.assertEqual(mul(-1, 1), -1)
        self.assertEqual(mul(100, -100), -10000)

    def test_mul2(self):
        self.assertRaises(TypeError, mul, 'a', 2)
