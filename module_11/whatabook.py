import mysql.connector
import pydantic
from abc import ABC, abstractmethod
from pydantic import BaseSettings
from configparser import ConfigParser
from enum import Enum

"""
    Title: pysports_queries.py
    Author: Patrick Loyd
    Date: Dec 8 2022
    Description: Whatabook program
"""

# Custom errors for common mistakes in program


class EnviromentNotSetError(Exception):
    def __init__(self, message="Environment variables not set"):
        super().__init__(message)


class ConfigNotSetError(Exception):
    def __init__(self, message="Configuration not set"):
        super().__init__(message)


class TableNotFoundError(Exception):
    def __init__(self, table_name):
        self.table_name = table_name
        message = f"{self.table_name} table not found"
        super().__init__(message)


class IllegalArgumentError(ValueError):
    def __init__(self, message="Invalid Choice for Menu"):
        super().__init__(message)

class InvalidUserError(Exception):
    def __init__(self, message="Invalid User"):
        super().__init__(message)


# Manages environment vairavles
# use pydantic to get username and password environment vairavles.
# using environment vairables adds an extra layer of security
# must set environment variables locally either using shell/terminal or a .env file
# using a .env file is recommended
class SQLEnvironment(BaseSettings):
    sql_user: str
    password: str

    class Config:
        env_file = ".env"


# Manages the connection and sql query configurations
# The configuration file will auto-generate if it is not found
# The default configurations should work for this project as long as the database is set up correctly
class SQLConfiguration:

    CONNECTION_SECTION = "CONNECTION"
    QUERY_SECTION = "QUERIES"
    BANNER_SECTION = "BANNERS"
    FILE = "config.ini"

    HOST = "HOST"
    DATABASE = "DATABASE"
    RAISE_ON_WARNINGS = "RAISE_ON_WARNINGS"

    @classmethod
    def create_config(cls, config_path):
        with open("config.txt") as config_handle:
            config_content = config_handle.read()

            with open(".config", "w") as config_file:
                config_file.write(config_content)

    @classmethod
    def load(cls, section):
        config = ConfigParser()
        config.read(cls.FILE)
        return config[section]

    @classmethod
    def load_connection_config(cls):
        return cls.load(cls.CONNECTION_SECTION)

    @classmethod
    def load_query_config(cls):
        return cls.load(cls.QUERY_SECTION)

    @classmethod
    def load_banner_config(cls):
        return cls.load(cls.BANNER_SECTION)


class SQLQueryCommands(Enum):
    try:
        sql_queries = SQLConfiguration.load_query_config()
    except KeyError:
        raise ConfigNotSetError

    get_books = eval(sql_queries["GET_BOOKS"])
    get_locations = eval(sql_queries["GET_LOCATIONS"])
    get_total_users = eval(sql_queries["GET_TOTAL_USERS"])
    get_wishlist_books = eval(sql_queries["GET_WISHLIST_BOOKS"])
    get_books_to_add = eval(sql_queries["GET_BOOKS_TO_ADD"])
    add_book_to_wishlist = eval(sql_queries["ADD_BOOK_TO_WISHLIST"])


# Context manager that will make a connection to the database on entry and close the connection on exit using the configuration file
class SQLConnection:
    def __init__(self):
        try:
            self.connection_config = SQLConfiguration.load_connection_config()
        except KeyError:
            raise ConfigNotSetError

        try:
            self.env = SQLEnvironment().dict()
        except pydantic.error_wrappers.ValidationError:
            raise EnviromentNotSetError

        self.config = {
            "user": self.env["sql_user"],
            "password": self.env["password"],
            "host": self.connection_config[SQLConfiguration.HOST],
            "database": self.connection_config[SQLConfiguration.DATABASE],
            "raise_on_warnings": self.connection_config.getboolean(
                SQLConfiguration.RAISE_ON_WARNINGS
            ),
        }

    def __enter__(self):
        self.db = mysql.connector.connect(**self.config)
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.close()


# Manage interfacing with the database
class SQLInterface:
    def __init__(self):
        pass

    from abc import ABC, abstractmethod

    def fetch(self, query):
        with SQLConnection() as database_connection:
            sql_cursor = database_connection.cursor()
            sql_cursor.execute(query)
            return sql_cursor.fetchall()

    def commit(self, query, data):
        with SQLConnection() as database_connection:
            sql_cursor = database_connection.cursor()
            sql_cursor.execute(query, data)
            database_connection.commit()

    def insert(self, query):
        with SQLConnection() as database_connection:
            sql_cursor = database_connection.cursor()
            sql_cursor.execute(query)
            database_connection.commit()


# Whatabook database documents
class Document(ABC):
    def __init__(self, banner, *values):
        self.format_string = banner.format(*values)

    @staticmethod
    @abstractmethod
    def to_object(query_table):
        pass

    def format(self):
        return self.format_string + "\n"


class WhatabookBanners(Enum):
    try:
        sql_banners = SQLConfiguration.load_banner_config()
    except KeyError:
        raise ConfigNotSetError

    get_books = eval(sql_banners["GET_BOOKS"])
    get_locations = eval(sql_banners["GET_LOCATIONS"])
    get_wishlist_books = eval(sql_banners["GET_WISHLIST_BOOKS"])
    get_books_to_add = eval(sql_banners["GET_BOOKS_TO_ADD"])


class User(Document):
    def __init__(self, first_name, last_name, user_id=None, banner=""):
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id
        super().__init__(banner, self.first_name, self.last_name)

    @staticmethod
    def to_object(query_table):
        (user_id, first_name, last_name) = query_table
        return User(first_name, last_name, user_id)

    def format(self):
        return super().format()


class Book(Document):

    # set raw strings for book to be formatted
    GET_BOOKS = WhatabookBanners.get_books.value
    GET_WISHLIST_BOOKS = WhatabookBanners.get_wishlist_books.value
    BOOKS_TO_ADD = WhatabookBanners.get_books_to_add.value

    def __init__(self, book_name, author, details, book_id=None, banner=GET_BOOKS):
        self.book_name = book_name
        self.author = author
        self.details = details
        self.book_id = book_id
        super().__init__(banner, self.book_name, self.author, self.details)

    @staticmethod
    def to_object(query_table):
        (book_id, book_name, author, details) = query_table
        return Book(book_name, author, details, book_id)

    @staticmethod
    def wishlist_book(query_table):
        (_, _, _, book_id, book_name, author, details) = query_table
        return Book(book_name, author, details, book_id, Book.GET_WISHLIST_BOOKS)

    @staticmethod
    def available_books(query_table):
        (book_id, book_name, author, details) = query_table
        return Book(book_name, author, details, book_id, Book.BOOKS_TO_ADD)

    def format(self):
        return super().format()


class Wishlist(Document):
    def __init__(self, user_id, book_id, wishlist_id=None, banner=""):
        self.user_id = user_id
        self.book_id = book_id
        self.wishlist_id = wishlist_id
        super().__init__(banner, self.user_id, self.book_id)

    @staticmethod
    def to_object(query_table):
        (user_id, book_id, wishlist_id) = query_table
        return Wishlist(user_id, book_id, wishlist_id)

    def format(self):
        return super().format()


class Store(Document):
    BANNER = WhatabookBanners.get_locations.value

    def __init__(self, locale, store_id=None, banner=BANNER):
        self.locale = locale
        self.store_id = store_id
        super().__init__(banner, self.locale)

    @staticmethod
    def to_object(query_table):
        (store_id, locale) = query_table
        return Store(locale, store_id)

    def format(self):
        return super().format()


class Whatabook(SQLInterface):
    def __init__(self):
        super().__init__()

    def get_books(self):
        query = SQLQueryCommands.get_books.value
        table = self.fetch(query)
        if not table:
            raise TableNotFoundError("book")
        results = "-- DISPLAYING BOOK LISTING --\n"
        for book in table:
            results += Book.to_object(book).format()
        return results

    def get_locations(self):
        query = SQLQueryCommands.get_locations.value
        table = self.fetch(query)
        if not table:
            raise TableNotFoundError("store")
        results = "-- DISPLAYING STORE LOCATIONS --\n"
        for store in table:
            results += Store.to_object(store).format()
        return results

    def get_total_users(self):
        query = SQLQueryCommands.get_total_users.value
        table = self.fetch(query)
        if not table:
            raise TableNotFoundError("user")
        return len(table)

    def validate_user_id(self, user_id):
        total_users = self.get_total_users()
        return True if 1 < user_id < total_users else False

    def get_wishlist_books(self, user_id):
        query = SQLQueryCommands.get_wishlist_books.value.format(user_id)
        table = self.fetch(query)
        if not table:
            raise TableNotFoundError("wishlist")
        results = "-- DISPLAYING WISHLIST ITEMS --\n"
        for book in table:
            results += Book.wishlist_book(book).format()
        return results

    def get_books_to_add(self, user_id):
        query = SQLQueryCommands.get_books_to_add.value.format(user_id)
        table = self.fetch(query)
        if not table:
            raise TableNotFoundError("book")
        results = "-- DISPLAYING AVAILABLE BOOKS --\n"
        for book in table:
            results += Book.available_books(book).format()
        return results

    def add_book_to_wishlist(self, user_id, book_id):
        query = SQLQueryCommands.add_book_to_wishlist.value.format(user_id, book_id)
        print(query)
        self.insert(query)


class WhatabookMenu(Whatabook):
    def __init__(self):
        self.max_menu_choices = 4
        self.max_account_menu_choices = 3
        super().__init__()

    def get_menu_choice(self):
        print("-- Main Menu --\n")

        print(
            "1. View Books\n2. View Store Locations\n3. My Account\n4. Exit Program\n"
        )

        try:
            choice = int(input("<Example enter: 1 for book listing>: "))
            if not 1 <= choice <= self.max_menu_choices:
                raise IllegalArgumentError
            return choice

        except IllegalArgumentError:
            return None

        except ValueError:
            return None

    def get_account_menu_choice(self):
        try:
            print("-- Customer Menu --\n")
            print("1. Wishlist\n2. Add Book\n3. Main Menu\n")
            account_option = int(input("<Example enter: 1 for wishlist>: "))
            if not 1 <= account_option <= self.max_account_menu_choices:
                raise IllegalArgumentError
            return account_option

        except IllegalArgumentError:
            return None

        except ValueError:
            return None

    def add_book_menu(self, user_id):
        try:
            book_id = int(input("Enter Book ID: "))
            self.add_book_to_wishlist(user_id, book_id)

        except ValueError:
            print("Invalid Book ID")

        finally:
            print("Book added successfully...")

    def my_account(self, user_id):
        # validate user ID
        try:
            if not self.validate_user_id(user_id):
                raise InvalidUserError
        except InvalidUserError:
            print("Invalid user id, try again...")
            raise

        account_loop = True
        while account_loop:
            account_menu_choice = self.get_account_menu_choice()
            if not account_menu_choice:
                print("Invalid choice, try again...")

            # finish each match case
            match account_menu_choice:
                case 1:
                    print(self.get_wishlist_books(user_id))
                    self.add_book_menu(user_id)

                case 2:
                    print(self.get_books_to_add(user_id))

                case 3:
                    account_loop = False


def main():
    whatabookmenu = WhatabookMenu()
    main_loop = True
    while main_loop:
        menu_choice = whatabookmenu.get_menu_choice()
        if not menu_choice:
            print("Invalid choice, try again...")

        match menu_choice:
            case 1:
                print(whatabookmenu.get_books())

            case 2:
                print(whatabookmenu.get_locations())

            case 3:
                try:
                    user_id = int(input("Enter User ID: "))
                    whatabookmenu.my_account(user_id)

                except ValueError:
                    print("Invalid user id, try again...")

                except Exception as e:
                    print(f"Error {e}: There was an issue logging in, try again...")

            case 4:
                main_loop = False
    print("Exiting Program...")


if __name__ == "__main__":
    main()
