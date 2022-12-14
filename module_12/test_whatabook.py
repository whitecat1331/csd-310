# file name should start with => test_ <= or end with => _test <= #
import unittest
from whatabook import Whatabook
from sys import maxsize

class TestCalculator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):  # run once before all test cases ###
        cls.whatabook = Whatabook()
        cls.default_user_id = 1
        cls.default_book_id = 1

    @classmethod
    def tearDownClass(cls):  # run once after all test cases ###
        pass

    def setUp(self):  # run before each test case ###
        pass

    def tearDown(self):  # run after each test case ###
        pass

    def test_get_books(self):
        result = self.whatabook.get_books()
        unexpected = None
        self.assertNotEquals(result, unexpected)

    def test_get_locations(self):
        result = self.whatabook.get_locations()
        unexpected = None
        self.assertNotEquals(result, unexpected)

    def test_get_total_users(self):
        result = self.whatabook.get_total_users()
        expected = 3
        self.assertEqual(result, expected)

    def test_validate_user_id(self):
        result = self.whatabook.validate_user_id(self.default_user_id)
        expected = True
        self.assertEquals(result, expected)

        user_id = -1
        result = self.whatabook.validate_user_id(user_id)
        expected = False
        self.assertEquals(result, expected)

        user_id = maxsize
        result = self.whatabook.validate_user_id(user_id)
        expected = False
        self.assertEqual(result, expected)

    def test_get_wishlist_books(self):
        result = self.whatabook.get_wishlist_books(self.default_user_id)
        unexpected = None
        self.assertNotEquals(result, unexpected)

    def test_get_books_to_add(self):
        result = self.whatabook.get_books_to_add(self.default_user_id)
        unexpected = None
        self.assertNotEquals(result, unexpected)

    def test_add_book_to_wishlist(self):
        self.whatabook.add_book_to_wishlist(self.default_user_id, self.default_book_id)

        









    
