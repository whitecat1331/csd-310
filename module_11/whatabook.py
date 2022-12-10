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
    FILE = ".config"

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
    show_wishlist = sql_queries["SHOW_WISHLIST"]


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
    BANNER = "Book Name: {}\nAuthor: {}\n"

    def __init__(self, User, Book, wishlist_id=None):
        self.user_id = User.user_id
        self.book_id = Book.book_id
        self.wishlist_id = wishlist_id
        super().__init__(self.BANNER, Book.book_name, Book.author)

    @staticmethod
    def to_object(query_tuple):
        (book_id, book_name, author, details) = query_tuple
        return Book(book_name, details, author, book_id)

    def format(self):
        return super().format()


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
            raise Exception("Book table not found")
        results = "-- DISPLAYING BOOK LISTING --\n"
        for book in table:
            results += f"{Book.to_object(book).format()}\n"
        return results

    def get_locations(self):
        query = SQLQueryCommands.show_locations.value
        table = self.fetch(query)
        if not table:
            raise Exception("Store table not found")
        results = "-- DISPLAYING STORE LOCATIONS --\n"
        for store in table:
            results += f"{Store.to_object(store).format()}\n"
        return results

    def get_total_users(self):
        query = SQLQueryCommands.show_user_ids.value
        table = self.fetch(query)
        if not table:
            raise Exception("User table not found")
        return len(table)

    def valiate_user_id(self, user_id):
        total_users = self.get_total_users()
        if not 0 < user_id < total_users:
            return False
        return True

    def show_wishlist(self):
        query = SQLQueryCommands.show_wishlist.value
        return query.format("does this work?")


def main():
    try:
        whatabook = Whatabook()
        print(whatabook.get_books())
        print(whatabook.get_locations())
        print(whatabook.valiate_user_id(1))
        print(whatabook.valiate_user_id(10))
        print(whatabook.show_wishlist())


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
