import unittest
from whatabook import WhatabookMenu
from unittest import mock
from sys import maxsize


class TestCalculator(unittest.TestCase):

    # run once before all test cases
    @classmethod
    def setUpClass(cls):
        cls.whataboookmenu = WhatabookMenu()
        cls.valid_choice = 1
        cls.invalid_no_choice = 0
        cls.invalid_negative_choice = -1
        cls.invalid_max_choice = maxsize

    # run once after all test cases
    @classmethod
    def tearDownClass(cls):
        pass

    # run before each test case
    def setUp(self):
        pass

    # run after each test case
    def tearDown(self):
        pass

    def test_show_menu(self):
        mock.builtins.input = lambda _: self.valid_choice
        result = self.whataboookmenu.show_menu()
        expected = 1
        self.assertEqual(result, expected)

        mock.builtins.input = lambda _: self.invalid_no_choice
        result = self.whataboookmenu.show_menu()
        expected = None
        self.assertEqual(result, expected)

        mock.builtins.input = lambda _: self.invalid_negative_choice
        result = self.whataboookmenu.show_menu()
        expected = None
        self.assertEqual(result, expected)

        mock.builtins.input = lambda _: self.invalid_max_choice
        result = self.whataboookmenu.show_menu()
        expected = None
        self.assertEqual(result, expected)

    def test_show_account_menu(self):
        mock.builtins.input = lambda _: self.valid_choice
        result = self.whataboookmenu.show_account_menu()
        expected = 1
        self.assertEqual(result, expected)

        mock.builtins.input = lambda _: self.invalid_no_choice
        result = self.whataboookmenu.show_account_menu()
        expected = None
        self.assertEqual(result, expected)

        mock.builtins.input = lambda _: self.invalid_negative_choice
        result = self.whataboookmenu.show_account_menu()
        expected = None
        self.assertEqual(result, expected)

        mock.builtins.input = lambda _: self.invalid_max_choice
        result = self.whataboookmenu.show_account_menu()
        expected = None
        self.assertEqual(result, expected)
