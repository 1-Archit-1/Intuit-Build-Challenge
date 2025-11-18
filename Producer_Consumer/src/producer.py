"""Producer thread - reads from source and puts items in queue."""

import threading
import queue
import time
from typing import List, Any

from .models import Item, ItemStatus

class Producer(threading.Thread):
    """
    Producer thread that reads items from a source and places them into queues.
    - Thread synchronization
    - Blocking queue operations
    - Graceful shutdown
    """
    
    def __init__(
        self, 
        name: str,
        source: List[Any], 
        shared_queue: queue.Queue,
        stop_event: threading.Event,
        production_delay: float = 0.1
    ):
        """
        Initialize the producer thread.
        """
        super().__init__(name=name, daemon=False)
        self.source = source
        self.shared_queue = shared_queue
        self.stop_event = stop_event
        self.production_delay = production_delay
        self.items_produced = 0
        self.lock = threading.Lock()
        
    def run(self):
        """
        Reads items from source and places them in the queue.
        """
        print(f"[{self.name}] Started - Processing {len(self.source)} items")
        
        for idx, data in enumerate(self.source):
            if self.stop_event.is_set():
                print(f"[{self.name}] Stop event received, shutting down...")
                break
            
            item = Item(
                id=idx,
                data=data,
                timestamp=time.time(),
                status=ItemStatus.PENDING
            )
            
            try:
                time.sleep(self.production_delay)
                
                self.shared_queue.put(item, timeout=5)  # Blocks if queue full
                item.status = ItemStatus.IN_QUEUE
                
                with self.lock:
                    self.items_produced += 1
                
                print(f"[{self.name}] Produced: {item} | Queue size: {self.shared_queue.qsize()}")
                
            except queue.Full:
                print(f"[{self.name}] ERROR: Queue full, couldn't produce {item}")
                break
            except Exception as e:
                print(f"[{self.name}] ERROR: {e}")
                break
        
        print(f"[{self.name}] Finished - Produced {self.items_produced} items")
    
    def get_stats(self) -> dict:
        """Return statistics about the producer"""
        with self.lock:
            return {
                'name': self.name,
                'items_produced': self.items_produced,
                'source_size': len(self.source)
            }
