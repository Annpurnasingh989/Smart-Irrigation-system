from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["smart_irrigation"]

farmers = db["farmers"]
predictions = db["predictions"]