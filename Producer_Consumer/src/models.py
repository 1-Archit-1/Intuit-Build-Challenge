"""This module contains the data structures used throughout the system."""

from enum import Enum
from typing import Any

class ItemStatus(Enum):
    """Status of items in the system"""
    PENDING = "pending"
    IN_QUEUE = "in_queue"
    CONSUMED = "consumed"

class Item:
    """
    Item being transferred from producer to consumer.
        id: Unique ID
        data: Payload
        timestamp: Creation Timestamp
        status: Current status of the item in pipeline
    """
    def __init__(self, id: int, data: Any, timestamp: float, status: ItemStatus = ItemStatus.PENDING):
        self.id = id
        self.data = data
        self.timestamp = timestamp
        self.status = status
    def __repr__(self):
        return f"Item(id={self.id}, data={self.data}, status={self.status.value})"
