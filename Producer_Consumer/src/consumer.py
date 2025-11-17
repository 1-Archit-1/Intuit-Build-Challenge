"""Consumer thread - reads from queue(s) and stores items."""

import threading
import queue
import time
from typing import List, Optional, Union

from .models import Item, ItemStatus


class Consumer(threading.Thread):
    """
    Consumer thread that reads items from one or more queues.
    
    Can consume from single queue and multiple queues (round-robin).
    
    - Thread synchronization
    - Blocking queue operations
    - Wait/notify mechanism through queue
    - Multi-queue round-robin consumption
    """
    
    def __init__(self,
                 name: str,
                 shared_queue: Union[queue.Queue, List[queue.Queue]],
                 destination: List[Item],
                 stop_event: threading.Event,
                 consumption_delay: float = 0.15,
                 max_items: Optional[int] = None):
        """
        Initialize the consumer thread.
        """
        super().__init__(name=name, daemon=False)
        
        if isinstance(shared_queue, list):
            self.queues = shared_queue
        else:
            self.queues = [shared_queue]
        
        self.destination = destination
        self.stop_event = stop_event
        self.consumption_delay = consumption_delay
        self.max_items = max_items
        self.items_consumed = 0
        self.lock = threading.Lock()
        self.queue_index = 0  # round-robin index for multi-queue
        
    def run(self):
        """
        Reads items from queue and stores them in destination.
        Uses round-robin for multiple queues.
        """
        num_queues = len(self.queues)
        print(f"[{self.name}] Started - Monitoring {num_queues} queue(s) ")
        
        consecutive_empty = 0
        max_consecutive_empty = num_queues * 2
        
        while not self.stop_event.is_set():
            if self.max_items and self.items_consumed >= self.max_items:
                print(f"[{self.name}] Reached max items limit ({self.max_items})")
                break
            
            try:
                current_queue = self.queues[self.queue_index]
                timeout = 1 if num_queues == 1 else 0.1
                item = current_queue.get(timeout=timeout)
                
                consecutive_empty = 0
                time.sleep(self.consumption_delay)
                item.status = ItemStatus.CONSUMED
                
                with self.lock:
                    self.destination.append(item)
                    self.items_consumed += 1
                
                current_queue.task_done()
                if num_queues == 1:
                    print(f"[{self.name}] Consumed: {item} | Queue size: {current_queue.qsize()}")
                else:
                    print(f"[{self.name}] Consumed: {item} from queue {self.queue_index}")
                
            except queue.Empty:
                consecutive_empty += 1
                if consecutive_empty >= max_consecutive_empty and self.stop_event.is_set():
                    break
            except Exception as e:
                print(f"[{self.name}] ERROR: {e}")
                break

            finally:
                self.queue_index = (self.queue_index + 1) % num_queues
        
        print(f"[{self.name}] Finished - Consumed {self.items_consumed} items")

    def get_stats(self) -> dict:
        """Return statistics about the consumer"""
        with self.lock:
            return {
                'name': self.name,
                'items_consumed': self.items_consumed,
                'destination_size': len(self.destination),
                'num_queues': len(self.queues)
            }
