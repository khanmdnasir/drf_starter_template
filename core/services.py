# services/base_service
import certifi
from abc import ABC, abstractmethod
from pymongo import MongoClient
from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from django.conf import settings

T = TypeVar('T', bound=BaseModel)


class BaseService(ABC, Generic[T]):
    def __init__(self, collection_name: str):
        self.client = MongoClient(
            f"mongodb+srv://{settings.MONGODB_SETTINGS['db_user']}:{settings.MONGODB_SETTINGS['db_password']}@{settings.MONGODB_SETTINGS['db_cluster_url']}/?retryWrites=true&w=majority",
            tlsCAFile=certifi.where())
        self.db = self.client[settings.MONGODB_SETTINGS['db_name']]
        self.collection = self.db[collection_name]

    @abstractmethod
    def pre_modification(self, data: dict) -> dict:
        pass

    @abstractmethod
    def post_modification(self, data: dict) -> dict:
        pass

    def insert_one(self, data: T) -> str:
        """Insert a Pydantic model into MongoDB"""
        result = self.collection.insert_one(data.model_dump())
        return str(result.inserted_id)

    def find_one(self, query: dict) -> dict:
        """Find a single document by a query"""
        result = self.collection.find_one(query)
        if result:
            result["_id"] = str(result["_id"])
        modify_result = self.post_modification(result)
        return modify_result

    def find_all(self, query: dict = {}) -> list:
        """Find all documents matching a query"""
        results = self.collection.find(query)
        result_list = []
        for result in results:
            result["_id"] = str(result["_id"])
            modify_result = self.post_modification(result)
            result_list.append(modify_result)
        return result_list

    def update_one(self, query: dict, update_data: T) -> dict:
        """Update a document based on a query"""
        result = self.collection.update_one(query, {"$set": update_data.model_dump()})
        return {"modified_count": result.modified_count}

    def delete_one(self, query: dict) -> dict:
        """Delete a document based on a query"""
        result = self.collection.delete_one(query)
        return {"deleted_count": result.deleted_count}
