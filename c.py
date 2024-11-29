import socket

# Function to display menu and get user input
def display_menu():
    print("\nPlease choose an option:")
    print("1. Check availability of a book")
    print("2. Borrow a book")
    print("3. Return a book")
    print("4. Exit")
    choice = input("Enter your choice: ")
    return choice

def client_program():
    # Connect to the server on localhost, port 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("localhost", 12345)

    try:
        client_socket.connect(server_address)
        print("Connected to the server.")
        
        # Receive the prompt for the username from the server
        welcome_message = client_socket.recv(1024).decode('utf-8')
        print(welcome_message)

        # Input username
        username = input("Enter your username: ")
        client_socket.send(username.encode('utf-8'))
        
        # Receive welcome message from the server
        response = client_socket.recv(1024).decode('utf-8')
        print(response)

        while True:
            # Display menu and get user input
            choice = display_menu()

            # Send the action choice to the server
            if choice == '1':  # Check availability
                book_name = input("Enter book name to check availability: ")
                client_socket.send(f"CHECK {book_name}".encode('utf-8'))
            
            elif choice == '2':  # Borrow a book
                book_name = input("Enter book name to borrow: ")
                client_socket.send(f"BORROW {book_name}".encode('utf-8'))
            
            elif choice == '3':  # Return a book
                book_name = input("Enter book name to return: ")
                client_socket.send(f"RETURN {book_name}".encode('utf-8'))
            
            elif choice == '4':  # Exit
                client_socket.send("EXIT".encode('utf-8'))
                print("Exiting...")
                break
            
            # Wait for server's response and print it
            server_response = client_socket.recv(1024).decode('utf-8')
            print(server_response)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    client_program()
