from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseRepository(ABC):
    """
    Base Repository Contract

    Enforces:
    - JSON-based IO
    - Standard CRUD interface
    - No silent failures
    """

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> str:
        """
        Insert a new record

        Returns:
            id (str): unique identifier of created record
        """
        pass

    @abstractmethod
    def get(self, record_id: str) -> Dict[str, Any]:
        """
        Fetch a record by ID
        """
        pass

    @abstractmethod
    def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a record

        Returns:
            success (bool)
        """
        pass

    @abstractmethod
    def delete(self, record_id: str) -> bool:
        """
        Delete a record

        Returns:
            success (bool)
        """
        pass
