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

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

    def insert(self):
        self.id = self.students.insert_one(self.to_dict()).inserted_id
        return f"Inserted student record {self.first_name} {self.last_name} into the {self.collection_name} collection with document_id {self.id}"


thor = Student("1007", "Thor", "Oakenshield")
spider_man = Student("1008", "Peter", "Parker")
hulk = Student("1009", "Bruce", "Banner")

print(thor.insert())
print(spider_man.insert())
print(hulk.insert())
