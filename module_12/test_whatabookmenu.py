import unittest
from whatabook import WhatabookMenu
from unittest.mock import patch
from sys import maxsize


class TestCalculator(unittest.TestCase):

    test_choices = [1, -1, 0, maxsize]
    # run once before all test cases
    @classmethod
    def setUpClass(cls):
        cls.whataboookmenu = WhatabookMenu()
        cls.default_user_id = 1
        cls.get_wishlist_choice = 1
        cls.add_book_choice = 2
        cls.exit_account = 3

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

    @patch("whatabook.input", side_effect=test_choices)
    def test_get_menu_choice(self, mock_input):
        result = self.whataboookmenu.get_menu_choice()
        expected = 1
        self.assertEqual(result, expected)

        result = self.whataboookmenu.get_menu_choice()
        expected = None
        self.assertEqual(result, expected)

        result = self.whataboookmenu.get_menu_choice()
        expected = None
        self.assertEqual(result, expected)

        result = self.whataboookmenu.get_menu_choice()
        expected = None
        self.assertEqual(result, expected)

    @patch("whatabook.input", side_effect=test_choices)
    def test_get_account_menu_choice(self, mock_input):
        result = self.whataboookmenu.get_account_menu_choice()
        expected = 1
        self.assertEqual(result, expected)

        result = self.whataboookmenu.get_account_menu_choice()
        expected = None
        self.assertEqual(result, expected)

        result = self.whataboookmenu.get_account_menu_choice()
        expected = None
        self.assertEqual(result, expected)

        result = self.whataboookmenu.get_account_menu_choice()
        expected = None
        self.assertEqual(result, expected)

    @patch("whatabook.input", side_effect=test_choices)
    def test_add_book_menu(self, mock_input):
        result = self.whataboookmenu.add_book_menu(self.default_user_id)
        expected = True
        self.assertEqual(result, expected)

        result = self.whataboookmenu.add_book_menu(self.default_user_id)
        expected = False
        self.assertEqual(result, expected)

        result = self.whataboookmenu.add_book_menu(self.default_user_id)
        expected = False
        self.assertEqual(result, expected)

        result = self.whataboookmenu.add_book_menu(self.default_user_id)
        expected = False
        self.assertEqual(result, expected)

    @patch("whatabook.input")
    def test_my_account(self, mock_input):
        exit_option = 3
        display_wishlist_option = [1, exit_option]
        add_book_option = [2, 1, exit_option]

        mock_input.return_value = exit_option
        self.whataboookmenu.my_account(self.default_user_id)

        mock_input.side_effect = display_wishlist_option
        self.whataboookmenu.my_account(self.default_user_id)

        # add default book id of 1
        test_add_book = add_book_option
        mock_input.side_effect = test_add_book
        self.whataboookmenu.my_account(self.default_user_id)

    @patch("whatabook.input")
    def test_main_menu(self, mock_input):
        exit_option = 4
        show_books_option = [1, exit_option]
        show_locations_option = [2, exit_option]
        add_book_option = [3, 1, 3, exit_option]

        mock_input.return_value = exit_option
        self.whataboookmenu.main_menu()

        mock_input.side_effect = show_books_option
        self.whataboookmenu.main_menu()

        mock_input.side_effect = show_locations_option
        self.whataboookmenu.main_menu()

        mock_input.side_effect = add_book_option
        self.whataboookmenu.main_menu()
