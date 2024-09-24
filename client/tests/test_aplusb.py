from aplusb import add
import unittest

class TestAdd(unittest.TestCase):
    def test_add1(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(100, -100), 0)
        
    def test_add2(self):
        self.assertRaises(TypeError, add, 'a', 2)

