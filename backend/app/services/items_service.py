# SRP: ItemService is responsible only for item CRUD business logic.
# DIP: Depends on IItemRepository (an abstraction) injected at construction
#      time, not on the concrete JsonItemRepository.
import uuid
from typing import List

from fastapi import HTTPException
from interfaces.repositories import IItemRepository
from schemas.item import Item, ItemCreate, ItemUpdate


class ItemService:
    """Handles all item business logic."""

    def __init__(self, item_repo: IItemRepository) -> None:
        self._repo = item_repo

    def list_items(self) -> List[Item]:
        return [Item(**it) for it in self._repo.load_all()]

    def create_item(self, payload: ItemCreate) -> Item:
        items = self._repo.load_all()
        new_id = str(uuid.uuid4())
        if any(it.get("id") == new_id for it in items):  # extremely unlikely, but safe
            raise HTTPException(status_code=409, detail="ID collision; retry.")
        new_item = self._build_item(new_id, payload)
        items.append(new_item.dict())
        self._repo.save_all(items)
        return new_item

    def get_item_by_id(self, item_id: str) -> Item:
        for it in self._repo.load_all():
            if it.get("id") == item_id:
                return Item(**it)
        raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")

    def update_item(self, item_id: str, payload: ItemUpdate) -> Item:
        items = self._repo.load_all()
        for idx, it in enumerate(items):
            if it.get("id") == item_id:
                updated = self._build_item(item_id, payload)
                items[idx] = updated.dict()
                self._repo.save_all(items)
                return updated
        raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")

    def delete_item(self, item_id: str) -> None:
        items = self._repo.load_all()
        new_items = [it for it in items if it.get("id") != item_id]
        if len(new_items) == len(items):
            raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")
        self._repo.save_all(new_items)

    def _build_item(self, item_id: str, payload: ItemCreate | ItemUpdate) -> Item:
        return Item(
            id=item_id,
            title=payload.title.strip(),
            category=payload.category.strip(),
            tags=payload.tags,
        )
