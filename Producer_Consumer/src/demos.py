"""Demo scenarios for producer-consumer pattern."""

import time

from .system import ProducerConsumerSystem


def demo_basic_pattern():
    print("\n--- Demo 1: Basic Pattern ---\n")
    
    source_data = [f"Data-{i}" for i in range(20)]
    destination = []
    system = ProducerConsumerSystem()
    system.add_queue("main", queue_size=5)
    
    system.add_producer("Producer-1", source_data, production_delay=0.1, queue_name="main")
    system.add_consumer("Consumer-1", destination, consumption_delay=0.15, queue_names="main")
    
    system.start()
    system.wait_for_completion()
    system.print_statistics()
    
    print(f"\n{len(destination)} items in destination")
    print(f"Sample: {destination[:3]}")


def demo_multiple_producers_consumers():
    print("\n--- Demo 2: Multiple Producers and Consumers ---\n")
    
    source1 = [f"P1-Data-{i}" for i in range(10)]
    source2 = [f"P2-Data-{i}" for i in range(10)]
    source3 = [f"P3-Data-{i}" for i in range(10)]
    
    destination1 = []
    destination2 = []
    system = ProducerConsumerSystem()
    system.add_queue("main", queue_size=15)
    
    system.add_producer("Producer-1", source1, production_delay=0.05, queue_name="main")
    system.add_producer("Producer-2", source2, production_delay=0.08, queue_name="main")
    system.add_producer("Producer-3", source3, production_delay=0.06, queue_name="main")
    
    system.add_consumer("Consumer-1", destination1, consumption_delay=0.1, max_items=15, queue_names="main")
    system.add_consumer("Consumer-2", destination2, consumption_delay=0.12, max_items=15, queue_names="main")
    
    system.start()
    system.wait_for_completion(timeout=30)
    system.print_statistics()
    
    print(f"\nDestination 1: {len(destination1)} items")
    print(f"Destination 2: {len(destination2)} items")
    print(f"Total: {len(destination1) + len(destination2)} items")


def demo_fast_producer_slow_consumer():
    print("\n--- Demo 3: Fast Producer, Slow Consumer ---\n")
    
    source_data = [f"FastData-{i}" for i in range(15)]
    destination = []
    
    system = ProducerConsumerSystem()
    system.add_queue("main", queue_size=3)
    
    system.add_producer("FastProducer", source_data, production_delay=0.02, queue_name="main")
    system.add_consumer("SlowConsumer", destination, consumption_delay=0.2, queue_names="main")
    
    system.start()
    system.wait_for_completion()
    system.print_statistics()


def demo_multiple_queues():
    print("\n--- Demo 4: Multiple Queues (Fan-in) ---\n")
    
    sensor1_data = [f"Sensor1-{i}" for i in range(5)]
    sensor2_data = [f"Sensor2-{i}" for i in range(5)]
    sensor3_data = [f"Sensor3-{i}" for i in range(5)]
    
    aggregated_destination = []
    
    system = ProducerConsumerSystem()
    system.add_queue("sensor1", queue_size=5)
    system.add_queue("sensor2", queue_size=5)
    system.add_queue("sensor3", queue_size=5)
    
    system.add_producer("Producer-S1", sensor1_data, production_delay=0.05, queue_name="sensor1")
    system.add_producer("Producer-S2", sensor2_data, production_delay=0.07, queue_name="sensor2")
    system.add_producer("Producer-S3", sensor3_data, production_delay=0.06, queue_name="sensor3")
    
    system.add_consumer("Aggregator", aggregated_destination, consumption_delay=0.08, 
                       queue_names=["sensor1", "sensor2", "sensor3"])
    
    system.start()
    system.wait_for_completion()
    system.print_statistics()
    
    print(f"\nAggregated {len(aggregated_destination)} items from 3 queues")
    print(f"Sample: {[str(item.data) for item in aggregated_destination[:6]]}")


def run_all_demos():
    print("\n=== Producer-Consumer Demos ===")
    
    demo_basic_pattern()
    time.sleep(1)
    
    demo_multiple_producers_consumers()
    time.sleep(1)
    
    demo_fast_producer_slow_consumer()
    time.sleep(1)
    
    demo_multiple_queues()
    
    print("\n=== Demos Complete ===")
