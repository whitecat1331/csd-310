import mysql.connector
import os
import pydantic
from pydantic import BaseSettings
from configparser import ConfigParser
from mysql.connector import errorcode

"""
    Title: pysports_queries.py
    Author: Patrick Loyd
    Date: 27 Nov 2022
    Description: Test program for executing queries against the pysports database. 
"""


class EnviromentNotSetError(Exception):
    def __init__(self, message="Environment variables not set"):
        super().__init__(message)


class ConfigNotSetError(Exception):
    def __init__(self, message="Configuration not set"):
        super().__init__(message)


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
            cls.RAISE_ON_WARNINGS: "true" if raise_on_warnings else "false",
        }

        if not os.path.isdir(cls.FILE):
            os.mkdir(cls.FILE)

        with open(config_path, "w") as config_file:
            config.write(config_file)

    @classmethod
    def load_config(cls):
        config = ConfigParser()
        config.read(cls.FILE)
        return config[cls.SECTION]


class Player:
    def __init__(self, player_id, first_name, last_name):
        self.player_id = player_id
        self.first_name = first_name
        self.last_name = last_name


class Team:
    def __init__(self, team_id, team_name, mascot):
        self.team_id = team_id
        self.team_name = team_name
        self.mascot = mascot


class SQLConnection:
    def __init__(self):
        try:
            self.config = MongoConfiguration.load_config()
        except KeyError:
            raise ConfigNotSetError

        try:
            self.env = SQLEnvironment().dict()
        except pydantic.error_wrappers.ValidationError:
            raise EnviromentNotSetError

        self.config = {
            "user": self.env["sql_user"],
            "password": self.env["password"],
            "host": self.config[MongoConfiguration.HOST],
            "database": self.config[MongoConfiguration.DATABASE],
            "raise_on_warnings": self.config.getboolean(
                MongoConfiguration.RAISE_ON_WARNINGS
            ),
        }

    def __enter__(self):
        self.db = mysql.connector.connect(**self.config)
        self.cursor = self.db.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.close()


class PySportsFormat:
    @staticmethod
    def teamsf(display_tag, teams):
        results = f"{display_tag}\n"
        for team in teams:
            results += "Team ID: {}\n  Team Name: {}\n  Mascot: {}\n".format(
                team[0], team[1], team[2]
            )

        return results

    @staticmethod
    def playersf(display_tag, players):
        results = f"{display_tag}\n"
        for player in players:
            results += "  Player ID: {}\n  First Name: {}\n  Last Name: {}\n  Team ID: {}\n".format(
                player[0], player[1], player[2], player[3]
            )

        return results

    @staticmethod
    def player_teamname_f(display_tag, join):
        results = f"{display_tag}\n"
        for column in join:
            results += "  Player ID: {}\n  First Name: {}\n  Last Name: {}\n  Team ID: {}\n".format(
                column[0], column[1], column[2], column[3]
            )
        return results


class PySports:
    def fetch(self, query, values=None):
        with SQLConnection() as sql:
            sql.execute(query, values)
            return sql.fetchall()

    def get_teams(self):
        query = "SELECT team_id, team_name, mascot FROM team"
        teams = self.fetch(query)
        if not teams:
            raise Exception("teams not found")
        team_tag = "-- DISPLAYING TEAM RECORDS --\n"
        results = PySportsFormat.teamsf(team_tag, teams)
        return results

    def get_players(self):
        query = "SELECT player_id, first_name, last_name, team_id FROM player"
        players = self.fetch(query)
        if not players:
            raise Exception("players not found")
        player_tag = "-- DISPLAYING PLAYER RECORDS --\n"
        results = PySportsFormat.playersf(player_tag, players)
        return results

    def player_teamname(self):
        query = "SELECT player_id, first_name, last_name, team_name FROM player INNER JOIN team ON player.team_id = team.team_id"
        join = self.fetch(query)
        if not join:
            raise Exception("join not found")
        player_teamname_tag = "-- DISPLAYING PLAYER RECORDS --"
        results = PySportsFormat.player_teamname_f(player_teamname_tag, join)
        return results

    # def insert_player(self, player):


def main():
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

        # print(pysports.get_teams())

        # select query for the player table
        # cursor.execute("SELECT player_id, first_name, last_name, team_id FROM player")

        # get the results from the cursor object
        # players = cursor.fetchall()

        # print ("\n  -- DISPLAYING PLAYER RECORDS --")

        # iterate over the players data set and display the results
        # for player in players:
        # print("  Player ID: {}\n  First Name: {}\n  Last Name: {}\n  Team ID: {}\n".format(player[0], player[1], player[2], player[3]))
        # print(pysports.get_players())

        # display the player and team join
        print(pysports.player_teamname())

        input("\n\n  Press any key to continue... ")

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
