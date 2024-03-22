# client.py

import socket

# Define the server's IP address and port
SERVER_IP = '172.24.232.119'  # Replace 'your_laptop_ip' with your laptop's IP address
SERVER_PORT = 55555          # Use the same port as in server.py

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((SERVER_IP, SERVER_PORT))

# Send data to the server
client_socket.send(b'Hello, server!')

# Receive data from the server
data = client_socket.recv(1024)
print('Received from server:', data.decode())

# Close the connection
client_socket.close()