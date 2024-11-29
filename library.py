import socket
import threading
import signal
import sys
import time
from collections import deque

# Sample books in the library
books = {'book1': 3, 'book2': 5, 'book3': 2}
book_lock = threading.Lock()

# This dictionary will store the username of the client
client_usernames = {}

# Flag to control server shutdown
server_running = True

# List of replica servers
replica_servers = [("localhost", 12346), ("localhost", 12347)]

# Vector clock: Each server maintains a clock with entries for each server
vector_clock = [0, 0, 0]  # Initially, the clocks are 0 for all servers (3 servers)

# Task queue to synchronize tasks based on logical clocks
task_queue = deque()

# Log to track user actions and tasks with their logical timestamps
task_log = []

# Leader variables
current_leader = None
election_in_progress = False
server_id = None  # Each server will have a unique ID

# Timeout for leader detection (in seconds)
leader_timeout = 5

def handle_client(client_socket, client_address, server_index):
    global vector_clock, task_queue, task_log, current_leader
    print(f"Connection established with {client_address}")

    try:
        # Prompt for username
        client_socket.send("Please enter your username:".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8').strip()
        client_usernames[client_address] = username
        
        # Inform the user that their username has been registered
        client_socket.send(f"Welcome, {username}! How can I assist you today?".encode('utf-8'))
        
        # Notify that the user has connected
        print(f"User '{username}' connected from {client_address}")
        
        while server_running:
            # Receive user input
            user_input = client_socket.recv(1024).decode('utf-8')
            if not user_input:
                break  # If no data is received, break the loop

            if user_input == "EXIT":
                print(f"{username} disconnected.")
                del client_usernames[client_address]  # Remove user from client list
                client_socket.close()
                break

            elif user_input.startswith("CHECK"):
                book_name = user_input.split(' ')[1]
                check_availability(book_name, client_socket, username, server_index)
            
            elif user_input.startswith("BORROW"):
                book_name = user_input.split(' ')[1]
                borrow_book(book_name, client_socket, username, server_index)
            
            elif user_input.startswith("RETURN"):
                book_name = user_input.split(' ')[1]
                return_book(book_name, client_socket, username, server_index)
            
            else:
                client_socket.send(f"{username}, Invalid option. Please try again.".encode('utf-8'))
    except Exception as e:
        print(f"Error while handling client {client_address}: {e}")
    finally:
        # When the client disconnects, notify the server
        if client_address in client_usernames:
            username = client_usernames[client_address]
            print(f"User '{username}' disconnected.")
            del client_usernames[client_address]
        client_socket.close()

def update_vector_clock(server_index):
    global vector_clock
    vector_clock[server_index] += 1
    print(f"Updated Vector Clock: {vector_clock}")  # Print vector clock after each update
    return vector_clock[:]

def check_availability(book_name, client_socket, username, server_index):
    with book_lock:
        updated_clock = update_vector_clock(server_index)  # Increment clock for this server's action
        if book_name in books and books[book_name] > 0:
            client_socket.send(f"{username}, {book_name} is available, {books[book_name]} copies left.".encode('utf-8'))
            task_log.append((username, "CHECK", book_name, updated_clock))  # Log the action with clock
            print_task_log()  # Print the task log here after the action
        else:
            client_socket.send(f"{username}, {book_name} is not available right now.".encode('utf-8'))
            task_log.append((username, "CHECK", book_name, updated_clock))
            print_task_log()

def borrow_book(book_name, client_socket, username, server_index):
    with book_lock:
        updated_clock = update_vector_clock(server_index)  # Increment clock for this server's action
        if book_name in books and books[book_name] > 0:
            books[book_name] -= 1
            client_socket.send(f"{username}, You have borrowed {book_name}. Enjoy reading!".encode('utf-8'))
            task_log.append((username, "BORROW", book_name, updated_clock))  # Log the action with clock
            print_task_log()  # Print the task log here after the action
            # Replicate data to all replicas
            replicate_data_to_replicas(f"BORROW {book_name}")
        else:
            client_socket.send(f"{username}, Sorry, {book_name} is currently unavailable.".encode('utf-8'))
            task_log.append((username, "BORROW", book_name, updated_clock))
            print_task_log()

def return_book(book_name, client_socket, username, server_index):
    with book_lock:
        updated_clock = update_vector_clock(server_index)  # Increment clock for this server's action
        if book_name in books:
            books[book_name] += 1
            client_socket.send(f"{username}, Thank you for returning {book_name}. Enjoy the rest of your day!".encode('utf-8'))
            task_log.append((username, "RETURN", book_name, updated_clock))  # Log the action with clock
            print_task_log()  # Print the task log here after the action
            # Replicate data to all replicas
            replicate_data_to_replicas(f"RETURN {book_name}")
        else:
            client_socket.send(f"{username}, Invalid book name {book_name}. Unable to return.".encode('utf-8'))
            task_log.append((username, "RETURN", book_name, updated_clock))
            print_task_log()

def replicate_data_to_replicas(data):
    for replica in replica_servers:
        try:
            # Connect to the replica server
            replica_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            replica_socket.connect(replica)
            replica_socket.send(data.encode('utf-8'))
            replica_socket.close()
            print(f"Data propagated to replica {replica}")
        except Exception as e:
            print(f"Error replicating data to {replica}: {e}")

def print_task_log():
    print("Task Log:")
    for entry in task_log:
        print(f"{entry[0]} performed {entry[1]} on {entry[2]} with vector clock {entry[3]}")

def election():
    global current_leader, election_in_progress, server_id

    # Start an election if not already in progress
    if election_in_progress:
        return

    election_in_progress = True
    print("Starting election process...")

    # Start sending election messages to higher ID servers
    for idx, server in enumerate(replica_servers):
        if idx > server_id:  # Send election message to higher ID servers
            try:
                # Connect to the server and send an election message
                election_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                election_socket.connect(server)
                election_socket.send("ELECTION".encode('utf-8'))
                election_socket.close()
            except:
                print(f"Server {server} did not respond to election request.")
    
    # Wait for a while to see if any server responds with 'I am the leader'
    time.sleep(leader_timeout)
    
    if current_leader is None:
        current_leader = server_id  # This server is now the leader
        print(f"Server {server_id} has been elected as the leader.")

def start_server(port, server_index):
    global server_running, current_leader, server_id
    server_id = server_index  # Assign unique ID to the server

    # Start the election if the server is the first to run
    if server_index == 0:
        election()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)

    print(f"Server running on port {port}...")
    
    while server_running:
        try:
            client_socket, client_address = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address, server_index)).start()
        except KeyboardInterrupt:
            server_running = False
            print("Server is shutting down.")
            break

    server.close()

def main():
    # Running three servers on different ports
    ports = [12345, 12346, 12347]
    threads = []

    for i, port in enumerate(ports):
        thread = threading.Thread(target=start_server, args=(port, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
