from configparser import ConfigParser
from pymongo import MongoClient
import os

class MongoConnectionError(Exception):
    def __init__(self, message="Error connecting to the MongoDB API"):
        super().__init__(message)


class ConfigurationLoadError(Exception):
    def __init__(self, message="Error Loading Configuration File"):
        super().__init__(message)


class ConfigurationSetupError(Exception):
    def __init__(self, message="Error Setting Up Configuration File"):
        super().__init__(message)


class DocumentNotFoundError(Exception):
    def __init__(self, message="Error locating document(s)"):
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

    def __init__(self, url, database, collection, username, password):
        self.url = url.format(username=username, password=password)
        self.client = MongoClient(self.url)
        self.db = self.client[database]
        self.collection = self.db[collection]
        self.collection_name = self.db.list_collection_names()[0]


class MongoAPI(MongoConnection):
    SCHEMA = "mongodb+srv://{username}:{password}@"
    CONFIG_PATH = "config/mongodb_connection.ini"

    # create config file if not exists
    try:
        if not os.path.exists(CONFIG_PATH):
            MongoConfiguration.create_config(CONFIG_PATH)
    except Exception as e:
        raise ConfigurationSetupError

    # load configuration file
    try:
        CONNECTION_CONFIG = MongoConfiguration.load_config(CONFIG_PATH)
        CONNECTION_PATH = CONNECTION_CONFIG[MongoConfiguration.PATH]
        USERNAME = CONNECTION_CONFIG[MongoConfiguration.USERNAME]
        PASSWORD = CONNECTION_CONFIG[MongoConfiguration.PASSWORD]
        URL = SCHEMA + str(CONNECTION_PATH)

    except Exception as e:
        raise ConfigurationLoadError

    def __init__(self, database, collection):
        try:
            super().__init__(self.URL, database, collection, self.USERNAME, self.PASSWORD)
        except Exception as e:
            raise MongoConnectionError

    # override
    # return an dictionary of the objects that are found
    def find(self):
        collection = self.collection.find({})
        if not collection:
            raise DocumentNotFoundError
        return collection

    # override
    def find_one(self, primary_key, key_value):
        document = self.collection.find_one({primary_key: key_value})
        if not document:
            raise DocumentNotFoundError
        return document

    # override
    def insert(self, document):
        return self.collection.insert_one(document).inserted_id

    # override
    def update_one(self, primary_key, key_value, new_property, new_value):
        self.collection.update_one(
            {primary_key: key_value}, {"$set": {new_property: new_value}}
        )


class StudentDocument:

    def __init__(self, student_id, first_name, last_name):
        self._id = student_id
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self):
        return {
            "student_id": self._id,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }


class StudentCollection(MongoAPI):
    DATABASE = "pytech"
    COLLECTION = "students"

    def __init__(self):
        super().__init__(self.DATABASE, self.COLLECTION)

    id = ""

    def find(self):
        students = super().find()
        results = " -- DISPLAYING STUDENTS DOCUMENTS FROM find() QUERY --\n"
        for student in students:
            results += f"Student ID: {student['student_id']}\nFirst Name: {student['first_name']}\nLast Name: {student['last_name']}\n\n"
        return results

    def find_one(self, student_id):
        student = super().find_one("student_id", student_id)
        results = f" -- DISPLAYING STUDENT DOCUMENT {student_id} --\n"
        results += f"Student ID: {student['student_id']}\nFirst Name: {student['first_name']}\nLast Name: {student['last_name']}\n"
        return results

    # adapt to inheritance
    def insert(self, StudentDocument):
        document_id = super().insert(StudentDocument.to_dict())
        return f"Inserted student record {StudentDocument._id} {StudentDocument.last_name} into the {self.collection_name} collection with document_id {document_id}"

    def update_one(self, key_value, property, value):
        super().update_one("student_id", key_value, property, value)


student_collection = StudentCollection()
print(student_collection.find())
student_collection.update_one("1007", "last_name", "Smith")
print(student_collection.find_one("1007"))
