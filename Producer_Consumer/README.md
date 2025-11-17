# Producer-Consumer Pattern with Thread Synchronization

A clean implementation of the producer-consumer pattern in Python using threads, blocking queues, and synchronization primitives.

## Features

- **Thread-safe** - Uses `queue.Queue`, `threading.Lock`, and `threading.Event`
- **Multiple queues** - Single Consumer class handles one or many queues
- **Blocking operations** - Proper backpressure and flow control
- **Graceful shutdown** - Coordinated cleanup across all threads

## Requirements
- Standard library only (no external dependencies)

## Usage

### Run Demos

```bash
python3 producer_consumer.py
```

### Run Tests

```bash
# Run all tests
python3 -m unittest tests.test_producer_consumer

# Verbose output
python3 -m unittest tests.test_producer_consumer -v

# Run specific test class
python3 -m unittest tests.test_producer_consumer.TestSystemSingleQueue

# Run individual test
python3 -m unittest tests.test_producer_consumer.TestBasicModels.test_item_has_correct_fields
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
# 3 producers → 3 queues → 1 consumer
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

## Project Structure

```
Intuit_challenge/
├── src/
│   ├── models.py          # Item dataclass, ItemStatus enum
│   ├── producer.py        # Producer thread
│   ├── consumer.py        # Consumer thread
│   ├── system.py          # ProducerConsumerSystem orchestrator
│   └── demos.py           # Demo scenarios
├── tests/
│   └── test_producer_consumer.py  # unit tests
├── producer_consumer.py   # Entry point
└── README.md
```

## Thread Synchronization

- **`queue.Queue`** - Blocking put/get operations
- **`threading.Lock`** - Protects shared state
- **`threading.Event`** - Signals for graceful shutdown
- **`task_done()` / `join()`** - Wait/notify pattern
