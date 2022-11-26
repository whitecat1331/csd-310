import mysql.connector
import os
from pydantic import BaseSettings
from configparser import ConfigParser
from mysql.connector import errorcode

"""
    Title: pysports_queries.py
    Author: Patrick Loyd
    Date: 27 Nov 2022
    Description: Test program for executing queries against the pysports database. 
"""

""" import statements """

# use pydantic to get username and password environment vairavles.
# Can also be set with .env file


class SQLEnvironment(BaseSettings):
    sql_user: str
    password: str

    class Config:
        env_file = ".env"


""" database config class """


class MongoConfiguration:

    SECTION = "CONNECTION"
    FILE = ".config"

    HOST = "HOST"
    DATABASE = "DATABASE"
    RAISE_ON_WARNINGS = "RAISE_ON_WARNINGS"

    @classmethod
    def create_config(cls, config_path):
        print("Enter the variables to set configuration")
        host = input("Username: ")
        database = input("Database: ")
        raise_on_warnings = input("Raise On Warnings? (y/n)").lower() == "y"

        config = ConfigParser()
        config[cls.SECTION] = {
                cls.HOST: host,
                cls.DATABASE: database,
                cls.RAISE_ON_WARNINGS: "true" if raise_on_warnings else "false"
                }

        if not os.path.isdir(cls.FILE):
            os.mkdir(cls.FILE)

        with open(config_path, 'w') as config_file:
            config.write(config_file)

    @classmethod
    def load_config(cls):
        config = ConfigParser()
        config.read(cls.FILE)
        return config[cls.SECTION]


class SQLConnection:
    def __init__(self):
        self.config = MongoConfiguration.load_config()
        self.env = SQLEnvironment().dict()
        self.config = {
            "user": self.env["sql_user"],
            "password": self.env["password"],
            "host": self.config[MongoConfiguration.HOST],
            "database": self.config[MongoConfiguration.DATABASE],
            "raise_on_warnings": self.config.getboolean(MongoConfiguration.RAISE_ON_WARNINGS)
        }

    def __enter__(self):
        self.db = mysql.connector.connect(**self.config)
        self.cursor = self.db.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.close()


class PySports:

    def fetch(self, query):
        with SQLConnection() as sql:
            sql.execute(query)
            return sql.fetchall()

    def display_teams(self):
        query = "SELECT team_id, team_name, mascot FROM team"
        teams = self.fetch(query)
        if not teams:
            raise Exception("teams not found")
        results = "-- DISPLAYING TEAM RECORDS --\n"
        for team in teams:
            results += "Team ID: {}\n  Team Name: {}\n  Mascot: {}\n".format(team[0], team[1], team[2])

        print(results)

    def display_players(self):
        query = "SELECT player_id, first_name, last_name, team_id FROM player"
        players = self.fetch(query)
        if not players:
            raise Exception("players not found")
        results = "-- DISPLAYING PLAYER RECORDS --\n"
        for player in players:
            results += "  Player ID: {}\n  First Name: {}\n  Last Name: {}\n  Team ID: {}\n".format(player[0], player[1], player[2], player[3])

        print(results)


try:
    pysports = PySports()
    # try/catch block for handling potential MySQL database errors

    # db = mysql.connector.connect(**config) # connect to the pysports database 

    # cursor = db.cursor()

    # select query from the team table 
    # cursor.execute("SELECT team_id, team_name, mascot FROM team")

    # get the results from the cursor object 
    # teams = cursor.fetchall()

    # print()
    
    # iterate over the teams data set and display the results 
    # for team in teams: 
        # print("  Team ID: {}\n  Team Name: {}\n  Mascot: {}\n".format(team[0], team[1], team[2]))

    pysports.display_teams()

    # select query for the player table 
    # cursor.execute("SELECT player_id, first_name, last_name, team_id FROM player")

    # get the results from the cursor object 
    # players = cursor.fetchall()

    # print ("\n  -- DISPLAYING PLAYER RECORDS --")

    # iterate over the players data set and display the results
    # for player in players:
        # print("  Player ID: {}\n  First Name: {}\n  Last Name: {}\n  Team ID: {}\n".format(player[0], player[1], player[2], player[3]))
    pysports.display_players()

    input("\n\n  Press any key to continue... ")

except mysql.connector.Error as err:
    """ handle errors """

    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("  The supplied username or password are invalid")

    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("  The specified database does not exist")

    else:
        print(err)
    raise

