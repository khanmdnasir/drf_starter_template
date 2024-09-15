# services/mongodb_service.py

import pymongo, certifi
from django.conf import settings


class MongoDBService:
    def __init__(self):
        self.client = pymongo.MongoClient(f"mongodb+srv://{settings.MONGODB_SETTINGS['db_user']}:{settings.MONGODB_SETTINGS['db_password']}@{settings.MONGODB_SETTINGS['db_cluster_url']}/?retryWrites=true&w=majority", tlsCAFile=certifi.where())
        self.db = self.client[settings.MONGODB_SETTINGS['db_name']]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def insert_one(self, collection_name, data):
        collection = self.get_collection(collection_name)
        result = collection.insert_one(data)
        return result.inserted_id

    def find_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def update_one(self, collection_name, query, update_data):
        collection = self.get_collection(collection_name)
        return collection.update_one(query, {"$set": update_data})

    def delete_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)

    def find_many(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return list(collection.find(query))
