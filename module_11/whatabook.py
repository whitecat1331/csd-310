import mysql.connector
import pydantic
from abc import ABC, abstractmethod
from pydantic import BaseSettings
from configparser import ConfigParser
from mysql.connector import errorcode as connector_errors
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


# Whatabook database documents
class Document(ABC):
    def __init__(self, banner, *values):
        self.format_string = banner.format(*values)

    @staticmethod
    @abstractmethod
    def to_object(query_tuple):
        pass

    def format(self):
        return self.format_string + '\n'


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
    def to_object(query_tuple):
        (user_id, first_name, last_name) = query_tuple
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
    def to_object(query_tuple):
        (book_id, book_name, author, details) = query_tuple
        return Book(book_name, author, details, book_id)

    @staticmethod
    def wishlist_book(query_tuple):
        (_, _, _, book_id, book_name, author, details) = query_tuple
        return Book(book_name, author, details, book_id, Book.GET_WISHLIST_BOOKS)

    def format(self):
        return super().format()


class Wishlist(Document):

    def __init__(self, user_id, book_id, wishlist_id=None, banner=""):
        self.user_id = user_id
        self.book_id = book_id
        self.wishlist_id = wishlist_id
        super().__init__(banner, self.user_id, self.book_id)

    @staticmethod
    def to_object(query_tuple):
        (user_id, book_id, wishlist_id) = query_tuple
        return Wishlist(user_id, book_id, wishlist_id)

    def format(self):
        return super().format()

    # @staticmethod
    # def wishlist_book(query_tuple):
    #     (_, _, _, book_id, book_name, author, details) = query_tuple
    #     return Book(book_name, author, details, book_id, Book.GET_WISHLIST_BOOKS)

    # def books_to_add(query_tuple):
    #     return Book.to_object(query_tuple)


class Store(Document):
    BANNER = WhatabookBanners.get_locations.value

    def __init__(self, locale, store_id=None, banner=BANNER):
        self.locale = locale
        self.store_id = store_id
        super().__init__(banner, self.locale)

    @staticmethod
    def to_object(query_tuple):
        (store_id, locale) = query_tuple
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

    def valiate_user_id(self, user_id):
        total_users = self.get_total_users()
        if not 0 < user_id < total_users:
            return False
        return True

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
            results += Book.to_object(book).format()
        return results
            


class WhatabookMenu:
    def __init__(self):
        pass

    def show_menu():
        print("-- Main Menu --\n")

        print(
            "1. View Books\n2. View Store Locations\n3. My Account\n4. Exit Program\n"
        )

        try:
            choice = int(input("      <Example enter: 1 for book listing>: "))
            return choice
        except ValueError:
            return None

    def show_account_menu(self):
        try:
            print("-- Customer Menu --\n")
            print("1. Wishlist\n2. Add Book\n3. Main Menu\n")
            account_option = int(input("<Example enter: 1 for wishlist>: "))
            return account_option
        except ValueError:
            return None


def main():
    try:
        whatabook = Whatabook()
        print(whatabook.get_books())
        print(whatabook.get_locations())
        print(whatabook.valiate_user_id(1))
        print(whatabook.get_total_users())
        print(whatabook.valiate_user_id(10))
        print(whatabook.get_wishlist_books(1))
        print(whatabook.get_books_to_add(1))

    except mysql.connector.Error as err:
        """handle errors"""

        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("  The supplied username or password are invalid")

        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("  The specified database does not exist")

        else:
            print(err)
        raise


if __name__ == "__main__":
    main()
