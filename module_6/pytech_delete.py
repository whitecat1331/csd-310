from pydantic import BaseSettings
from pymongo import MongoClient

REQUIRED_SETTINGS = ["STUDENT_COLLECTION_URL", "USERNAME", "PASSWORD"]


class MongoEnvironment(BaseSettings):
    student_collection_url: str
    username: str
    password: str

    class Config:
        env_file = ".env"


class MongoEnvoronmentError(Exception):
    def __init__(self, message="Set Environment Variables: "):
        self.message = message
        settings = ', '.join(str(setting) for setting in REQUIRED_SETTINGS)
        self.message = message + settings
        super().__init__(self.message)


class MongoConnectionError(Exception):
    def __init__(self, message="Error connecting to the MongoDB API"):
        super().__init__(message)


try:
    CONNECTION_SETTINGS = MongoEnvironment().dict()
except Exception as e:
    raise MongoEnvoronmentError


"""
class ConfigurationLoadError(Exception):
    def __init__(self, message="Error Loading Configuration File"):
        super().__init__(message)


class ConfigurationSetupError(Exception):
    def __init__(self, message="Error Setting Up Configuration File"):
        super().__init__(message)
"""


class DocumentNotFoundError(Exception):
    def __init__(self, message="Error locating document(s)"):
        super().__init__(message)


# might implement later with different configuration
"""
class MongoConfiguration:
    PATH = "MONGODB_COLLECTION_PATH"
    USERNAME = "MONGODB_USERNAME"
    PASSWORD = "MONGODB_PASSWORD"
    DIRECTORY = ".env"
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
"""


class MongoConnection():

    def __init__(self, url, database, collection):
        self.url = url
        self.client = MongoClient(self.url)
        self.db = self.client[database]
        self.collection = self.db[collection]
        self.collection_name = self.collection.name


class MongoAPI(MongoConnection):
    CONFIG_PATH = "config/mongodb_connection.ini"

    def __init__(self, url, database, collection):
        try:
            super().__init__(url, database, collection)
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

    # override
    def delete_one(self, _id, value):
        self.collection.delete_one({_id: value})


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
    URL = CONNECTION_SETTINGS['student_collection_url']
    URL = URL.replace("username", CONNECTION_SETTINGS['username'])
    URL = URL.replace("<password>", CONNECTION_SETTINGS['password'])

    def __init__(self):
        super().__init__(self.URL, self.DATABASE, self.COLLECTION)

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

    def delete_one(self, student_id):
        super().delete_one("student_id", student_id)


student_collection = StudentCollection()
loki = StudentDocument("1010", "Many", "Laufeyson")

# Call the find() method and display the results to the terminal window.
print(student_collection.find())

# Call the insert_one() method and Insert a new document into the pytech collection with student_id 1010.
print(student_collection.insert(loki))

# Call the find_one() method and display the results to the terminal window.
print(student_collection.find_one(loki._id))

# Call the delete_one() method by student_id 1010.
student_collection.delete_one(loki._id)

# Call the find() method and display the results to the terminal window.
print(student_collection.find())
