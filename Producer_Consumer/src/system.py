"""System for producer-consumer threads."""

import queue
import threading
import time
from typing import List, Optional, Any, Dict, Union

from .models import Item
from .producer import Producer
from .consumer import Consumer


class ProducerConsumerSystem:
    """
    Producer-consumer system with flexible queue assignment.
    - Create multiple named queues
    - Route producers to specific queues
    - Route consumers to one or multiple queues
    """
    
    def __init__(self):
        """Initialize the producer-consumer system."""
        self.queues: Dict[str, queue.Queue] = {}
        self.stop_event = threading.Event()
        self.producers: List[Producer] = []
        self.consumers: List[Consumer] = []
        self.start_time = None
        self.end_time = None
    
    def add_queue(self, queue_name: str, queue_size: int = 10) -> queue.Queue:
        """
        Add a named queue to the system.
        """
        if queue_name in self.queues:
            raise ValueError(f"Queue '{queue_name}' already exists")
        
        self.queues[queue_name] = queue.Queue(maxsize=queue_size)
        return self.queues[queue_name]
    
    def get_queue(self, queue_name: str) -> queue.Queue:
        """Get a queue by name"""
        if queue_name not in self.queues:
            raise ValueError(f"Queue '{queue_name}' does not exist")
        return self.queues[queue_name]
        
    def add_producer(self, 
                     name: str,
                     source: List[Any],
                     production_delay: float = 0.1,
                     queue_name: str = None) -> Producer:
        """
        Add a producer to the system.
        """
        if queue_name is None:
            raise ValueError("queue_name is required")
        target_queue = self.get_queue(queue_name)
        producer = Producer(
            name=name,
            source=source,
            shared_queue=target_queue,
            stop_event=self.stop_event,
            production_delay=production_delay
        )
        self.producers.append(producer)
        return producer
    
    def add_consumer(
        self,
        name: str,
        destination: List[Item],
        consumption_delay: float = 0.15,
        max_items: Optional[int] = None,
        queue_names: Union[str, List[str]] = None
    ) -> Consumer:
        """
        Add a consumer to the system.
        """
        if queue_names is None:
            raise ValueError("queue_names is required")
            
        if isinstance(queue_names, str):
            target_queue = self.get_queue(queue_names)
        else:
            target_queue = [self.get_queue(qn) for qn in queue_names]
        
        consumer = Consumer(
            name=name,
            shared_queue=target_queue,
            destination=destination,
            stop_event=self.stop_event,
            consumption_delay=consumption_delay,
            max_items=max_items
        )
        
        self.consumers.append(consumer)
        return consumer
    
    def start(self):
        """Start all producer and consumer threads"""
        print(f"\nStarting system: {len(self.producers)} producer(s), {len(self.consumers)} consumer(s)")
        
        self.start_time = time.time()
        
        for producer in self.producers:
            producer.start()
        for consumer in self.consumers:
            consumer.start()
    
    def wait_for_completion(self, timeout: Optional[float] = None):
        """Wait for all threads to complete."""
        for producer in self.producers:
            producer.join(timeout=timeout)
        
        for qname, q in self.queues.items():
            q.join()
        
        self.stop_event.set()
        
        for consumer in self.consumers:
            consumer.join(timeout=timeout)
        
        self.end_time = time.time()
    
    def stop(self):
        """Gracefully stop all threads"""
        self.stop_event.set()
        
        for producer in self.producers:
            producer.join(timeout=5)
        
        for consumer in self.consumers:
            consumer.join(timeout=5)
        
        self.end_time = time.time()
    
    def get_statistics(self) -> dict:
        """Get comprehensive system statistics"""
        duration = (self.end_time - self.start_time) if self.end_time else 0
        
        producer_stats = [p.get_stats() for p in self.producers]
        consumer_stats = [c.get_stats() for c in self.consumers]
        
        total_produced = sum(p['items_produced'] for p in producer_stats)
        total_consumed = sum(c['items_consumed'] for c in consumer_stats)
        
        # Get remaining items in all queues
        queue_stats = {qname: q.qsize() for qname, q in self.queues.items()}
        total_queue_remaining = sum(queue_stats.values())
        
        return {
            'duration': duration,
            'total_produced': total_produced,
            'total_consumed': total_consumed,
            'total_queue_remaining': total_queue_remaining,
            'queue_stats': queue_stats,
            'producers': producer_stats,
            'consumers': consumer_stats
        }
    
    def print_statistics(self):
        """Print formatted system statistics"""
        stats = self.get_statistics()
        
        print(f"\n--- Stats ---")
        print(f"Duration: {stats['duration']:.2f}s")
        print(f"Produced: {stats['total_produced']}, Consumed: {stats['total_consumed']}")
        
        if stats['total_queue_remaining'] > 0:
            print(f"Remaining in queues: {stats['total_queue_remaining']}")
        
        if len(self.producers) > 1:
            for p_stat in stats['producers']:
                print(f"  {p_stat['name']}: {p_stat['items_produced']}/{p_stat['source_size']}")
        
        if len(self.consumers) > 1:
            for c_stat in stats['consumers']:
                print(f"  {c_stat['name']}: {c_stat['items_consumed']}")
