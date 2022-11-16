from configparser import ConfigParser
from pymongo import MongoClient
import os


class StudentConnectionError(Exception):
    def __init__(self, message="Error connecting to the MongoDB API"):
        super().__init__(message)


class ConfigurationLoadError(Exception):
    def __init__(self, message="Error Loading Configuration File"):
        super().__init__(message)


class ConfigurationSetupError(Exception):
    def __init__(self, message="Error Setting Up Configuration File"):
        super().__init__(message)


class MongoConfiguration:
    PATH = "MONGODB_COLLECTION_PATH"
    USERNAME = "MONGODB_USERNAME"
    PASSWORD = "MONGODB_PASSWORD"
    DIRECTORY = "config"
    SECTION = "CONNECTION"

    @classmethod
    def create_config(cls, config_path):
        print("Enter the variables to set configuration")
        collection_path = input("Collection Path: ")
        username = input("Username: ")
        password = input("Password: ")

        config = ConfigParser()
        config[cls.SECTION] = {
                cls.PATH: collection_path,
                cls.USERNAME: username,
                cls.PASSWORD: password
                }

        if not os.path.isdir(cls.DIRECTORY):
            os.mkdir(cls.DIRECTORY)

        with open(config_path, 'w') as config_file:
            config.write(config_file)

    @classmethod
    def load_config(cls, config_path):
        config = ConfigParser()
        config.read(config_path)
        return config[cls.SECTION]


class MongoConnection:

    def __init__(self, url, username, password):
        self.url = url.format(username=username, password=password)
        self.client = MongoClient(self.url)
        self.db = self.client.pytech
        self.students = self.db.students
        self.collection_name = self.db.list_collection_names()[0]


class StudentAPI:
    id = ""
    config_path = "config/mongodb_connection.ini"
    SCHEMA = "mongodb+srv://{username}:{password}@"

    # username and password environment variables must be set for connection to work
    try:
        if not os.path.exists(config_path):
            MongoConfiguration.create_config(config_path)
    except Exception as e:
        raise ConfigurationSetupError

    try:
        CONNECTION_CONFIG = MongoConfiguration.load_config(config_path)
        CONNECTION_PATH = CONNECTION_CONFIG[MongoConfiguration.PATH]
        USERNAME = CONNECTION_CONFIG[MongoConfiguration.USERNAME]
        PASSWORD = CONNECTION_CONFIG[MongoConfiguration.PASSWORD]
        URL = SCHEMA + str(CONNECTION_PATH)

    except Exception as e:
        raise ConfigurationLoadError

    try:
        connection = MongoConnection(URL, USERNAME, PASSWORD)

    except Exception as e:
        raise StudentConnectionError

    def __init__(self, student_id, first_name, last_name):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def find(cls):
        results = f" -- DISPLAYING STUDENTS DOCUMENTS FROM find() QUERY --\n"
        for student in cls.connection.students.find({}):
            results += f"Student ID: {student['student_id']}\nFirst Name: {student['first_name']}\nLast Name: {student['last_name']}\n\n"
        return results

    @classmethod
    def find_one(cls, student_id):
        results = f" -- DISPLAYING STUDENT DOCUMENT {student_id} --\n"
        student = cls.connection.students.find_one({"student_id": student_id})
        results += f"Student ID: {student['student_id']}\nFirst Name: {student['first_name']}\nLast Name: {student['last_name']}\n"
        return results

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

    def insert(self):
        self.id = self.connection.students.insert_one(self.to_dict()).inserted_id
        return f"Inserted student record {self.first_name} {self.last_name} into the {self.connection.collection_name} collection with document_id {self.id}"

    @classmethod
    def update_one(cls, student_id, property, value):
        cls.connection.students.update_one(
            {"student_id": student_id}, {"$set": {property: value}}
        )


print(StudentAPI.find())
# StudentAPI.update_one("1007", "last_name", "Odinson")
print(StudentAPI.find_one("1007"))
