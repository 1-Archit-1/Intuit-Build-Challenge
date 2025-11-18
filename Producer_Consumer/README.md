# Producer-Consumer Pattern with Thread Synchronization

A clean implementation of the producer-consumer pattern in Python using threads, blocking queues, and synchronization primitives.

## Features

- **Thread-safe** 
- **Multiple queues** - Handles one or many queues
- **Blocking operations** - Proper backpressure and flow control
- **Graceful shutdown** - Coordinated cleanup across all threads

## Requirements
- pytest

## Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv analysis_env

# Activate virtual environment
# On Linux/Mac:
source analysis_env/bin/activate

# On Windows:
prod_con_env\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Run Demos

The project includes 4 demo scenarios

```bash
python3 producer_consumer.py
```

**Demo 1: Basic Pattern**
- Single producer, queue, single consumer

**Demo 2: Multiple Producers and Consumers**
- 3 producers, shared queue, 2 consumers

**Demo 3: Fast Producer, Slow Consumer**
- Fast producer with small queue size
- queue blocking behavior

**Demo 4: Multiple Queues**
- 3 producers, 3 separate queues, 1 consumer(round robin)

### Run Tests

```bash
# Run all tests
pytest tests/test_producer_consumer.py

# Verbose output
pytest tests/test_producer_consumer.py -v

# Run specific test function
pytest tests/test_producer_consumer.py::test_item_has_correct_fields


# Show detailed output with print statements
pytest tests/test_producer_consumer.py -v -s
```

## Quick Start

```python
from src.system import ProducerConsumerSystem

# Create system and add queue
system = ProducerConsumerSystem()
system.add_queue("main", 10)

# Add producer and consumer
source = [f"item-{i}" for i in range(20)]
dest = []

system.add_producer("P1", source, 0.1, queue_name="main")
system.add_consumer("C1", dest, 0.1, queue_names="main")

# Run
system.start()
system.wait_for_completion()
system.print_statistics()
```

### Multi-Queue

```python
# 3 producers -> 3 queues -> 1 consumer
system = ProducerConsumerSystem()
system.add_queue("q1", 5)
system.add_queue("q2", 5)
system.add_queue("q3", 5)

system.add_producer("P1", data1, 0.01, queue_name="q1")
system.add_producer("P2", data2, 0.01, queue_name="q2")
system.add_producer("P3", data3, 0.01, queue_name="q3")

# Consumer reads from all 3 queues (round-robin)
system.add_consumer("C1", dest, 0.01, queue_names=["q1", "q2", "q3"])

system.start()
system.wait_for_completion()
```
