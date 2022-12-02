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


class PlayerDocument:
    def __init__(self, first_name, last_name, player_id=None):
        self.first_name = first_name
        self.last_name = last_name
        self.player_id = player_id


class TeamDocument:
    def __init__(self, team_name, mascot, team_id=None):
        self.team_name = team_name
        self.mascot = mascot
        self.team_id = team_id


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
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.close()


class PySportsFormat:
    @staticmethod
    def teamsf(display_tag, teams):
        results = f"{display_tag}\n"
        for team in teams:
            results += "Team ID: {}\n  Team Name: {}\n  Mascot: {}\n\n".format(
                team[0], team[1], team[2]
            )
        results += '\n'

        return results

    @staticmethod
    def playersf(display_tag, players):
        results = f"{display_tag}\n"
        for player in players:
            results += "  Player ID: {}\n  First Name: {}\n  Last Name: {}\n  Team ID: {}\n\n".format(
                player[0], player[1], player[2], player[3]
            )
        return results

    @staticmethod
    def player_teamname_f(display_tag, join):
        results = f"{display_tag}\n"
        for column in join:
            results += "  Player ID: {}\n  First Name: {}\n  Last Name: {}\n  Team ID: {}\n\n".format(
                column[0], column[1], column[2], column[3]
            )
        results += '\n'
        return results


class PySports:
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

    def get_players_teamname(self, player_teamname_tag="-- DISPLAYING PLAYER RECORDS --"):
        query = "SELECT player_id, first_name, last_name, team_name FROM player INNER JOIN team ON player.team_id = team.team_id"
        join = self.fetch(query)
        if not join:
            raise Exception("join not found")
        results = PySportsFormat.player_teamname_f(player_teamname_tag, join)
        return results

    def insert_player(self, player, team):
        if not team.team_id:
            raise Exception("Team ID not Set")
        query = (
                "INSERT INTO player (first_name, last_name, team_id) " +
                "VALUES (%s, %s, %s);"
             )
        data = (player.first_name, player.last_name, team.team_id)
        # execute query
        self.commit(query, data)
        # return results
        insert_players_tag = "-- DISPLAYING PLAYERS AFTER INSERT --"
        results = self.get_players_teamname(player_teamname_tag=insert_players_tag)
        return results

    def update_player_team(self, previous_player, new_player, team):
        if not team.team_id:
            raise Exception("Team ID not Set")
        query = (
                "UPDATE player SET " +
                f"team_id = {team.team_id}, " +
                f"first_name = '{new_player.first_name}', " +
                f"last_name = '{new_player.last_name}' " +
                f"WHERE first_name = '{previous_player.first_name}'"
            )
        self.fetch(query)
        update_player_tag = " -- DISPLAYING PLAYERS AFTER UPDATE --"
        results = self.get_players_teamname(player_teamname_tag=update_player_tag)
        return results

    def delete_player(self, player):
        query = f"DELETE FROM player WHERE first_name = '{player.first_name}'"
        self.fetch(query)
        delete_players_tag = "-- DISPLAYING PLAYERS AFTER DELETE --"
        results = self.get_players_teamname(player_teamname_tag=delete_players_tag)
        return results


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
        smeagol = PlayerDocument("Smeagol", "Shire Folk")
        gollum = PlayerDocument("Gollum", "Ring Stealer")

        gandolf = TeamDocument("Team Gandolf", "White Wizzards", 1)
        souron = TeamDocument("Team Souron", "Orcs", 2)

        print(pysports.get_players_teamname())
        print(pysports.insert_player(smeagol, gandolf))
        print(pysports.update_player_team(smeagol, gollum, souron))
        print(pysports.delete_player(gollum))

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
