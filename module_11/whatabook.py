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
    SQL_QUERY_SECTION = "QUERIES"
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
        return cls.load(cls.SQL_QUERY_SECTION)


class SQLQueryCommands(Enum):
    try:
        sql_queries = SQLConfiguration.load_query_config()
    except KeyError:
        raise ConfigNotSetError

    show_books = sql_queries["SHOW_BOOKS"]
    show_locations = sql_queries["SHOW_LOCATIONS"]
    show_user_ids = sql_queries["SHOW_USER_IDS"]
    show_wishlist_book = sql_queries["SHOW_WISHLIST_BOOK"]


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
        return self.format_string


class User(Document):
    BANNER = "First Name: {}\nLast Name: {}\n"

    def __init__(self, first_name, last_name, user_id=None):
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id
        super().__init__(self.BANNER, self.first_name, self.last_name)

    @staticmethod
    def to_object(query_tuple):
        (user_id, first_name, last_name) = query_tuple
        return User(first_name, last_name, user_id)

    def format(self):
        return super().format()


class Book(Document):
    BANNER = "Book Name: {}\nAuthor: {}\nDetails: {}\n"
    WISHLIST_BOOK_BANNER = "Book Name: {}\nAuthor: {}\n"

    def __init__(self, book_name, author, details, book_id=None):
        self.book_name = book_name
        self.author = author
        self.details = details
        self.book_id = book_id
        super().__init__(self.BANNER, self.book_name, self.author, self.details)

    @staticmethod
    def to_object(query_tuple):
        (book_id, book_name, author, details) = query_tuple
        return Book(book_name, author, details, book_id)

    def format(self):
        return super().format()


class Wishlist(Document):
    BANNER = "User ID: {}\nBook ID: {}\n"

    def __init__(self, user_id, book_id, wishlist_id=None):
        self.user_id = user_id
        self.book_id = book_id
        self.wishlist_id = wishlist_id
        super().__init__(self.BANNER, self.user_id, self.book_id)

    @staticmethod
    def to_object(query_tuple):
        (user_id, book_id, wishlist_id) = query_tuple
        return Wishlist(user_id, book_id, wishlist_id)

    def format(self):
        return super().format()

    @staticmethod
    def format_book(query_tuple):
        (_, _, _, _, book_name, author) = query_tuple
        book_banner = Book.WISHLIST_BOOK_BANNER
        return book_banner.format(book_name, author)


class Store(Document):
    BANNER = "Locale: {}\n"

    def __init__(self, locale, store_id=None):
        self.locale = locale
        self.store_id = store_id
        super().__init__(self.BANNER, self.locale)

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
        query = SQLQueryCommands.show_books.value
        table = self.fetch(query)
        if not table:
            raise TableNotFoundError("book")
        results = "-- DISPLAYING BOOK LISTING --\n"
        for book in table:
            results += f"{Book.to_object(book).format()}\n"
        return results

    def get_locations(self):
        query = SQLQueryCommands.show_locations.value
        table = self.fetch(query)
        if not table:
            raise TableNotFoundError("store")
        results = "-- DISPLAYING STORE LOCATIONS --\n"
        for store in table:
            results += f"{Store.to_object(store).format()}\n"
        return results

    def get_total_users(self):
        query = SQLQueryCommands.show_user_ids.value
        table = self.fetch(query)
        if not table:
            raise TableNotFoundError("user")
        return len(table)

    def valiate_user_id(self, user_id):
        total_users = self.get_total_users()
        if not 0 < user_id < total_users:
            return False
        return True

    def show_wishlist_book(self, user_id):
        query = SQLQueryCommands.show_wishlist_book.value.format(user_id)
        table = self.fetch(query)
        if not table:
            raise TableNotFoundError("wishlist")
        results = "-- DISPLAYING WISHLIST ITEMS --\n"
        for book in table:
            results += Wishlist.format_book(book)
        return results


class WhatabookMenu:
    def __init__(self):
        pass

    def show_menu():
        print("-- Main Menu --\n")

        print("1. View Books\n2. View Store Locations\n3. My Account\n4. Exit Program\n")

        try:
            choice = int(input('      <Example enter: 1 for book listing>: '))
            return choice
        except ValueError:
            print("\n  Invalid number, program terminated...\n")
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
        print(whatabook.valiate_user_id(10))
        print(whatabook.show_wishlist_book(1))

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
