# README for Distributed Library Management System

## Overview

This project is a **Distributed Library Management System** implemented using Python. It uses **multithreading**, **socket programming**, and **vector clocks** for handling concurrency and maintaining synchronization across replica servers.

### Key Features:
1. **Client-Server Architecture**:
   - Clients can check book availability, borrow books, and return books.
   - The server manages the library's inventory and handles client requests.
   
2. **Distributed System**:
   - Multiple servers handle client requests in a distributed manner.
   - Replica servers synchronize data to ensure consistency.

3. **Concurrency Control**:
   - Thread-safe operations for book inventory using locks.
   - Vector clocks maintain logical time for distributed events.

4. **Leader Election**:
   - Implements a simple leader election process to designate a leader among servers.

5. **Replication**:
   - Data changes are propagated to replica servers for consistency.

---

## File Structure

### 1. **Server Code** (`server.py`)
   - **Tasks**:
     - Handles client connections.
     - Manages library inventory (`books` dictionary).
     - Ensures thread-safe operations with `threading.Lock`.
     - Updates vector clocks for each operation.
     - Logs user actions with timestamps.
   - **Leader Election**:
     - Coordinates leader election among servers.
   - **Replication**:
     - Sends data changes to replicas.

### 2. **Client Code** (`client.py`)
   - **Tasks**:
     - Connects to the server.
     - Sends commands like `CHECK`, `BORROW`, and `RETURN`.
     - Receives responses from the server.

---

## Prerequisites

1. Python 3.x installed.
2. Basic knowledge of Python threading and socket programming.

---

## Setup and Execution

### 1. **Run the Servers**
   - Each server runs on a unique port.
   - Start the servers with:
     ```bash
     python server.py
     ```
     The servers will bind to the following ports by default:
     - Main server: `12345`
     - Replica 1: `12346`
     - Replica 2: `12347`

### 2. **Run the Client**
   - Start the client with:
     ```bash
     python client.py
     ```
   - The client connects to the main server at `localhost:12345`.

---

## Usage Instructions

### For Clients:
1. **Login**: Enter your username when prompted.
2. **Commands**:
   - **Check Availability**:
     - Choose option `1` and enter the book name.
   - **Borrow a Book**:
     - Choose option `2` and enter the book name.
   - **Return a Book**:
     - Choose option `3` and enter the book name.
   - **Exit**:
     - Choose option `4` to disconnect.

---

## System Design

### Vector Clocks:
- Each server maintains a vector clock to track the logical order of events.
- On each action (e.g., borrow, return), the server updates its vector clock and synchronizes it with replicas.

### Leader Election:
- Based on server IDs.
- A timeout mechanism ensures automatic leader re-election if the leader is unresponsive.

### Thread-Safety:
- Uses Python's `threading.Lock` to ensure safe concurrent access to shared resources like the `books` dictionary.

---

## Known Issues and Limitations

1. **Scalability**:
   - The system currently handles a limited number of clients and servers.
2. **Fault Tolerance**:
   - Replica synchronization does not handle partial failures robustly.

---

## Future Improvements

1. **Enhanced Leader Election**:
   - Use more sophisticated algorithms like the Bully algorithm or Paxos.
2. **Persistent Storage**:
   - Store book data in a database instead of memory.
3. **Load Balancing**:
   - Distribute client requests across servers dynamically.
4. **GUI for Clients**:
   - Add a graphical user interface for a better user experience.

---

## Credits

Developed as a demonstration of **distributed systems** concepts using Python.
