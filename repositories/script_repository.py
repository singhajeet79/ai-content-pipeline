from typing import Dict, Any

from repositories.mongo_repository import MongoRepository


class ScriptRepository(MongoRepository):
    """
    Repository for storing script outputs

    Collection: scripts
    """

    def __init__(self):
        super().__init__(collection_name="scripts")

    def create(self, data: Dict[str, Any]) -> str:
        """
        Override to enforce minimal structure
        """
        if "script" not in data:
            raise ValueError("Script data must contain 'script' field")

        return super().create(data)
