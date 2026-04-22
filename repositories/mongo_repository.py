from typing import Dict, Any
from bson import ObjectId

from repositories.base_repository import BaseRepository
from db.mongo_client import MongoDBClient


class MongoRepository(BaseRepository):
    """
    MongoDB Repository Implementation

    - Works with a single collection
    - Enforces JSON IO
    """

    def __init__(self, collection_name: str):
        client = MongoDBClient()
        self.collection = client.get_collection(collection_name)

    def create(self, data: Dict[str, Any]) -> str:
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def get(self, record_id: str) -> Dict[str, Any]:
        if not ObjectId.is_valid(record_id):
            raise ValueError("Invalid ObjectId")

        result = self.collection.find_one({"_id": ObjectId(record_id)})

        if not result:
            raise ValueError("Record not found")

        result["_id"] = str(result["_id"])
        return result

    def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(record_id):
            raise ValueError("Invalid ObjectId")

        result = self.collection.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": data}
        )

        return result.modified_count > 0

    def delete(self, record_id: str) -> bool:
        if not ObjectId.is_valid(record_id):
            raise ValueError("Invalid ObjectId")

        result = self.collection.delete_one({"_id": ObjectId(record_id)})
        return result.deleted_count > 0
