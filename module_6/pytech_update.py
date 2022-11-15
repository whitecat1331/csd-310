from pymongo import MongoClient
from os import getenv


class EnvironmentNotFound(Exception):
    pass


class StudentConnectionError(Exception):
    pass


class StudentConnection:
    def __init__(self, url, username, password):
        self.url = url.format(username=username, password=password)
        self.client = MongoClient(self.url)
        self.db = self.client.pytech
        self.students = self.db.students
        self.collection_name = self.db.list_collection_names()[0]


class StudentAPI:
    id = ""
    # username and password environment variables must be set for connection to work
    SCHEMA = "mongodb+srv://{username}:{password}@"
    CONNECTION_PATH = getenv("MONGODB_COLLECTION_PATH")
    USERNAME = getenv("MONGODB_USERNAME")
    PASSWORD = getenv("MONGODB_PASSWORD")
    if not (USERNAME or PASSWORD or CONNECTION_PATH):
        raise EnvironmentNotFound(
            "Environment variables MONGODB_USERNAME, MONGODB_PASSWORD, and MONGODB_COLLECTION_PATH must be set"
        )

    URL = SCHEMA + str(CONNECTION_PATH)

    try:
        connection = StudentConnection(URL, USERNAME, PASSWORD)

    except Exception as e:
        raise StudentConnectionError("Error connecting to the MongoDB API")

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
        results = f" -- DISPLAYING STUDENTS DOCUMENTS FROM find() QUERY --\n"
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


print(StudentAPI.find())
print(StudentAPI.find_one("1007"))
