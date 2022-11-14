from pymongo import MongoClient

url = "mongodb+srv://admin:admin@cluster0.jia3bcs.mongodb.net/pytech"

client = MongoClient(url)

db = client.pytech

output = f"-- Pytech Collection List --\n{db.list_collection_names()}"
print(output)
