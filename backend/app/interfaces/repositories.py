# ISP: Each repository interface is narrow and focused on a single entity type.
# DIP: Services depend on these abstractions, not on concrete JSON implementations.
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IUserRepository(ABC):
    @abstractmethod
    def load_all(self) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def save_all(self, users: List[Dict[str, Any]]) -> None:
        ...


class ISessionRepository(ABC):
    @abstractmethod
    def load_all(self) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def save_all(self, sessions: List[Dict[str, Any]]) -> None:
        ...


class IItemRepository(ABC):
    @abstractmethod
    def load_all(self) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def save_all(self, items: List[Dict[str, Any]]) -> None:
        ...
