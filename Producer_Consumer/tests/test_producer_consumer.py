"""Tests for producer-consumer pattern"""

import unittest
import time
import queue
import threading

from src.models import Item, ItemStatus
from src.producer import Producer
from src.consumer import Consumer
from src.system import ProducerConsumerSystem


class TestBasicModels(unittest.TestCase):
    """Test basic data models"""
    def test_item_has_correct_fields(self):
        item = Item(id=1, data="test", timestamp=123.45)
        self.assertEqual(item.id, 1)
        self.assertEqual(item.data, "test")
        self.assertEqual(item.status, ItemStatus.PENDING)


class TestProducerThread(unittest.TestCase):
    """Test Producer thread behavior"""
    
    def test_producer_sends_all_items_to_queue(self):
        source = ["A", "B", "C"]
        q = queue.Queue(maxsize=10)
        stop = threading.Event()
        
        producer = Producer("P1", source, q, stop, production_delay=0.01)
        producer.start()
        producer.join(timeout=2)
        
        self.assertEqual(producer.items_produced, 3)
        self.assertEqual(q.qsize(), 3)
    
    def test_producer_stops_when_signaled(self):
        source = [f"item{i}" for i in range(50)]
        q = queue.Queue(maxsize=10)
        stop = threading.Event()
        
        producer = Producer("P1", source, q, stop, production_delay=0.01)
        producer.start()
        time.sleep(0.1)
        stop.set()
        producer.join(timeout=2)
        
        self.assertLess(producer.items_produced, 50)


class TestConsumerThread(unittest.TestCase):
    """Test Consumer thread behavior"""
    
    def test_consumer_gets_all_items_from_queue(self):
        q = queue.Queue(maxsize=10)
        dest = []
        stop = threading.Event()
        
        for i in range(3):
            q.put(Item(id=i, data=f"item{i}", timestamp=time.time()))
        
        consumer = Consumer("C1", q, dest, stop, consumption_delay=0.01)
        consumer.start()
        time.sleep(0.2)
        stop.set()
        consumer.join(timeout=2)
        
        self.assertEqual(len(dest), 3)
        self.assertEqual(consumer.items_consumed, 3)
    
    def test_consumer_respects_max_items_limit(self):
        q = queue.Queue(maxsize=10)
        dest = []
        stop = threading.Event()
        
        for i in range(10):
            q.put(Item(id=i, data=f"item{i}", timestamp=time.time()))
        
        consumer = Consumer("C1", q, dest, stop, consumption_delay=0.01, max_items=5)
        consumer.start()
        consumer.join(timeout=2)
        
        self.assertEqual(consumer.items_consumed, 5)


class TestSystemSingleQueue(unittest.TestCase):
    """Test system with single queue"""
    
    def test_one_producer_one_consumer_transfers_all_items(self):
        """1P->Q->1C: All items should be transferred"""
        source = [f"data{i}" for i in range(10)]
        dest = []
        
        system = ProducerConsumerSystem()
        system.add_queue("main", 5)
        system.add_producer("P1", source, 0.01, queue_name="main")
        system.add_consumer("C1", dest, 0.01, queue_names="main")
        
        system.start()
        system.wait_for_completion(timeout=5)
        
        self.assertEqual(len(dest), 10)
        stats = system.get_statistics()
        self.assertEqual(stats['total_produced'], 10)
        self.assertEqual(stats['total_consumed'], 10)
    
    def test_two_producers_one_consumer_transfers_all_items(self):
        """2P->Q->1C: All items from both producers consumed"""
        source1 = [f"p1-{i}" for i in range(5)]
        source2 = [f"p2-{i}" for i in range(5)]
        dest = []
        
        system = ProducerConsumerSystem()
        system.add_queue("main", 10)
        system.add_producer("P1", source1, 0.01, queue_name="main")
        system.add_producer("P2", source2, 0.01, queue_name="main")
        system.add_consumer("C1", dest, 0.01, queue_names="main")
        
        system.start()
        system.wait_for_completion(timeout=5)
        
        self.assertEqual(len(dest), 10)
    
    def test_one_producer_two_consumers_distributes_items(self):
        """1P->Q->2C: Items distributed between consumers"""
        source = [f"data{i}" for i in range(20)]
        dest1, dest2 = [], []
        
        system = ProducerConsumerSystem()
        system.add_queue("main", 10)
        system.add_producer("P1", source, 0.01, queue_name="main")
        system.add_consumer("C1", dest1, 0.01, max_items=10, queue_names="main")
        system.add_consumer("C2", dest2, 0.01, max_items=10, queue_names="main")
        
        system.start()
        system.wait_for_completion(timeout=5)
        
        self.assertEqual(len(dest1) + len(dest2), 20)


class TestSystemMultiQueue(unittest.TestCase):
    """Test system with multiple queues"""
    
    def test_consumer_reads_from_multiple_queues_round_robin(self):
        """3P->3Q->1C: Consumer reads from all queues"""
        data1 = [f"Q1-{i}" for i in range(3)]
        data2 = [f"Q2-{i}" for i in range(3)]
        data3 = [f"Q3-{i}" for i in range(3)]
        dest = []
        
        system = ProducerConsumerSystem()
        system.add_queue("q1", 5)
        system.add_queue("q2", 5)
        system.add_queue("q3", 5)
        
        system.add_producer("P1", data1, 0.01, queue_name="q1")
        system.add_producer("P2", data2, 0.01, queue_name="q2")
        system.add_producer("P3", data3, 0.01, queue_name="q3")
        system.add_consumer("C1", dest, 0.01, queue_names=["q1", "q2", "q3"])
        
        system.start()
        system.wait_for_completion(timeout=5)
        
        self.assertEqual(len(dest), 9)


class TestThreadSafety(unittest.TestCase):
    """Test thread synchronization"""
    
    def test_queue_blocks_when_full(self):
        source = ["item1", "item2", "item3"]
        q = queue.Queue(maxsize=2)
        stop = threading.Event()
        dest = []
        
        producer = Producer("P1", source, q, stop, production_delay=0.01)
        consumer = Consumer("C1", q, dest, stop, consumption_delay=0.01, max_items=3)
        
        producer.start()
        time.sleep(0.15)
        
        self.assertEqual(q.qsize(), 2)  # queue full, producer blocked
        
        consumer.start()
        producer.join(timeout=2)
        consumer.join(timeout=2)
        
        self.assertEqual(len(dest), 3)
        self.assertEqual(producer.items_produced, 3)
    
    def test_no_data_loss_with_concurrent_access(self):
        """Multiple threads should not lose or duplicate data"""
        source1 = [f"p1-{i}" for i in range(20)]
        source2 = [f"p2-{i}" for i in range(20)]
        dest1, dest2 = [], []
        
        system = ProducerConsumerSystem()
        system.add_queue("main", 10)
        system.add_producer("P1", source1, 0.001, queue_name="main")
        system.add_producer("P2", source2, 0.001, queue_name="main")
        system.add_consumer("C1", dest1, 0.001, max_items=20, queue_names="main")
        system.add_consumer("C2", dest2, 0.001, max_items=20, queue_names="main")
        
        system.start()
        system.wait_for_completion(timeout=10)
        
        self.assertEqual(len(dest1) + len(dest2), 40)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases"""
    def test_very_small_queue_size_works(self):
        source = [f"data{i}" for i in range(5)]
        dest = []
        
        system = ProducerConsumerSystem()
        system.add_queue("main", 1)
        system.add_producer("P1", source, 0.01, queue_name="main")
        system.add_consumer("C1", dest, 0.01, queue_names="main")
        
        system.start()
        system.wait_for_completion(timeout=5)
        
        self.assertEqual(len(dest), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
