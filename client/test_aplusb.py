from aplusb import add, mul
import unittest

class TestAdd(unittest.TestCase):
    def test_add1(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(100, -100), 0)
        
    def test_add2(self):
        self.assertRaises(TypeError, add, 'a', 2)

class TestMul(unittest.TestCase):
    def test_mul1(self):
        self.assertEqual(mul(2, 3), 6)
        self.assertEqual(mul(0, 0), 0)
        self.assertEqual(mul(-1, 1), -1)
        self.assertEqual(mul(100, -100), -10000)
        
    def test_mul2(self):
        self.assertRaises(TypeError, mul, 'a', 2)
