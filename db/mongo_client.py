from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os


class MongoDBClient:
    """
    MongoDB Client Wrapper
    - Single connection per process
    - Config-driven
    - Fail-fast behavior
    """

    _client = None

    def __init__(self, uri: str = None, db_name: str = None):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("MONGO_DB_NAME", "ai_pipeline")

        if MongoDBClient._client is None:
            try:
                MongoDBClient._client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
                # Force connection check
                MongoDBClient._client.admin.command("ping")
                print("✅ MongoDB Connected")

            except ConnectionFailure as e:
                raise RuntimeError(f"❌ MongoDB connection failed: {e}")

        self.client = MongoDBClient._client
        self.db = self.client[self.db_name]

    def get_collection(self, name: str):
        return self.db[name]
