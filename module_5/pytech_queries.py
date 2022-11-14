from pymongo import MongoClient


class Student:
    id = ""
    url = "mongodb+srv://admin:admin@cluster0.jia3bcs.mongodb.net/pytech"
    client = MongoClient(url)
    db = client.pytech
    students = db.students
    collection_name = db.list_collection_names()[0]

    def __init__(self, student_id, first_name, last_name):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def find(cls):
        results = f" -- DISPLAYING STUDENTS DOCUMENTS FROM find() QUERY --\n"
        for student in cls.students.find({}):
            results += f"Student ID: {student['student_id']}\nFirst Name: {student['first_name']}\nLast Name: {student['last_name']}\n\n"
        return results

    @classmethod
    def find_one(cls, student_id):
        results = f" -- DISPLAYING STUDENTS DOCUMENTS FROM find() QUERY --\n"
        student = cls.students.find_one({"student_id": student_id})
        results += f"Student ID: {student['student_id']}\nFirst Name: {student['first_name']}\nLast Name: {student['last_name']}\n"
        return results

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

    def insert(self):
        self.id = self.students.insert_one(self.to_dict()).inserted_id
        return f"Inserted student record {self.first_name} {self.last_name} into the {self.collection_name} collection with document_id {self.id}"


print(Student.find())
print(Student.find_one("1007"))
