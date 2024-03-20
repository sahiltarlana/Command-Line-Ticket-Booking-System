import socket
import threading
import sqlite3

class TicketBookingSystem:
    def __init__(self):
        pass

    def connect_to_db(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT, password TEXT)''')
        return conn, cursor

    def register_user(self, conn, cursor, username, email, password):
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            return "Email already registered. Please choose another one."
        print("here it starts")
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        return "Registration successful."

    def login(self, cursor, email, password):
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        if user:
            print(user['id'])
            return "Login successful."
        return "Invalid email or password."

def handle_client(client_socket, ticket_system):
    conn, cursor = ticket_system.connect_to_db()
    while True:
        request = client_socket.recv(1024).decode()
        if not request:
            break
        request = request.split(" ")
        if request[0] == "register":
            username = request[1]
            email = request[2]
            password = request[3]
            response = ticket_system.register_user(conn, cursor, username, email, password)
        elif request[0] == "login":
            email = request[1]
            password = request[2]
            response = ticket_system.login(cursor, email, password)
        else:
            response = "Invalid command."
        client_socket.send(response.encode())
    conn.close()
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen(5)

    print("Server started. Listening for connections...")

    ticket_system = TicketBookingSystem()
    while True:
        client_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, ticket_system))
        client_thread.start()

if __name__ == "__main__":
    start_server()