import socket
import threading
import sqlite3
from datetime import date
import time
import random

class TicketBookingSystem:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor2 = self.conn.cursor()
        self.create_tables()
        self.semaphore = threading.Semaphore()  # Initialize the semaphore

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT, password TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bus
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT, available_tickets INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bookings
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, bus_id INTEGER, user_id INTEGER, num_tickets INTEGER,
                             FOREIGN KEY(bus_id) REFERENCES bus(id),
                             FOREIGN KEY(user_id) REFERENCES users(id))''')

    def register_user(self, username, email, password):
        with self.semaphore:  # Acquire the semaphore before executing the critical section
            self.cursor.execute("SELECT * FROM users WHERE email=?", (email,))
            if self.cursor.fetchone():
                return "Email already registered. Please choose another one."
            self.cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            self.conn.commit()
        return "Registration successful."

    def login(self, email, password):
        with self.semaphore:  # Acquire the semaphore before executing the critical section
            self.cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            user = self.cursor.fetchone()
            print(user[0])
            if user:
                return f"Login successful. user id :{user[0]}" , user[0]
        # return "Invalid email or password.", None

    def create_bus(self, name, date, available_tickets):
        with self.semaphore:  # Acquire the semaphore before executing the critical section
            self.cursor.execute("INSERT INTO bus (name, date, available_tickets) VALUES (?, ?, ?)", (name, date, available_tickets))
            self.conn.commit()
        return "bus created successfully."

    def book_ticket(self, bus_id, user_id, num_tickets):
        i = random.randint(1, 10)
        time.sleep(i)
        for k in range(i):
            print(f"{k}")
        with self.semaphore:  # Acquire the semaphore before executing the critical section
            self.cursor.execute("SELECT available_tickets FROM bus WHERE id=?", (bus_id,))
            available_tickets = self.cursor.fetchone()['available_tickets']
            if available_tickets >= num_tickets:
                self.cursor.execute("INSERT INTO bookings (bus_id, user_id, num_tickets) VALUES (?, ?, ?)", (bus_id, user_id, num_tickets))
                self.cursor.execute("UPDATE bus SET available_tickets=? WHERE id=?", (available_tickets - num_tickets, bus_id))
                self.conn.commit()
                return "Booking successful. | Booking ID : " + str(self.cursor.lastrowid)
        return "Not enough tickets available."

    def cancel_booking(self, booking_id):
        with self.semaphore:  # Acquire the semaphore before executing the critical section
            self.cursor.execute("SELECT bus_id, num_tickets FROM bookings WHERE id=?", (booking_id,))
            result = self.cursor.fetchone()
            if result:
                bus_id, num_tickets = result['bus_id'], result['num_tickets']
                self.cursor.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
                self.cursor.execute("UPDATE bus SET available_tickets=available_tickets+? WHERE id=?", (num_tickets, bus_id))
                self.conn.commit()
                return "Booking canceled successfully."
        return "Invalid booking ID."

    def show_bus(self):
        # self.cursor2.execute("SELECT name, date, available_tickets FROM bus WHERE date >= ?", (str(date.today()),))
        # bus = self.cursor2.fetchall()
        # bus_list = "\n".join([f"{row['name']} ({row['date']}) - {row['available_tickets']} available" for row in bus])
        # return bus_list or "No upcoming bus."

        # with self.semaphore:  # Acquire the semaphore before executing the critical section
        self.cursor2.execute("SELECT id, name, date, available_tickets FROM bus WHERE date >= ?", (str(date.today()),))
        bus = self.cursor2.fetchall()
        bus_list = "\n".join([f"bus_id : {row['id']} \t {row['name']} \t ({row['date']}) \t {row['available_tickets']} available" for row in bus])
        return bus_list or "No upcoming bus."

def handle_client(client_socket, ticket_system):
    while True:
        request = client_socket.recv(1024).decode()
        if not request:
            break
        request = request.split(" ")
        if request[0] == "register":
            username = request[1]
            email = request[2]
            password = request[3]
            response = ticket_system.register_user(username, email, password)
        elif request[0] == "login":
            email = request[1]
            password = request[2]
            response, user_id = ticket_system.login(email, password)
            # print(user_id)
            # response = ticket_system.login(email, password)
        elif request[0] == "create_bus":
            name = request[1]
            date = request[2]
            available_tickets = int(request[3])
            response = ticket_system.create_bus(name, date, available_tickets)
        elif request[0] == "book_ticket":
            user_id = int(request[1])
            bus_id = int(request[2])
            num_tickets = int(request[3])
            response = ticket_system.book_ticket(bus_id, user_id, num_tickets)
        elif request[0] == "cancel_booking":
            booking_id = int(request[1])
            response = ticket_system.cancel_booking(booking_id)
        elif request[0] == "show_bus":
            response = ticket_system.show_bus()
        else:
            response = "Invalid command."
        client_socket.send(response.encode())
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen(5)

    print("Server started. Listening for connections...")

    ticket_system = TicketBookingSystem('ticket_booking.db')
    while True:
        client_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, ticket_system))
        client_thread.start()

if __name__ == "__main__":
    start_server()