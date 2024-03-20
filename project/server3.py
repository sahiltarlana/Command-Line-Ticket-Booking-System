import socket
import threading
import sqlite3
from datetime import date

class TicketBookingSystem:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.semaphore = threading.Semaphore()  # Initialize the semaphore

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT, password TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS events
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT, available_tickets INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bookings
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER, user_id INTEGER, num_tickets INTEGER,
                             FOREIGN KEY(event_id) REFERENCES events(id),
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
        # with self.semaphore:  # Acquire the semaphore before executing the critical section
            self.cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            user = self.cursor.fetchone()
            print(user[0])
            if user:
                return "Login successful." , user[0]
        # return "Invalid email or password.", None

    def create_event(self, name, date, available_tickets):
        with self.semaphore:  # Acquire the semaphore before executing the critical section
            self.cursor.execute("INSERT INTO events (name, date, available_tickets) VALUES (?, ?, ?)", (name, date, available_tickets))
            self.conn.commit()
        return "Event created successfully."

    def book_ticket(self, event_id, user_id, num_tickets):
        with self.semaphore:  # Acquire the semaphore before executing the critical section
            self.cursor.execute("SELECT available_tickets FROM events WHERE id=?", (event_id,))
            available_tickets = self.cursor.fetchone()['available_tickets']
            if available_tickets >= num_tickets:
                self.cursor.execute("INSERT INTO bookings (event_id, user_id, num_tickets) VALUES (?, ?, ?)", (event_id, user_id, num_tickets))
                self.cursor.execute("UPDATE events SET available_tickets=? WHERE id=?", (available_tickets - num_tickets, event_id))
                self.conn.commit()
                return "Booking successful."
        return "Not enough tickets available."

    def cancel_booking(self, booking_id):
        with self.semaphore:  # Acquire the semaphore before executing the critical section
            self.cursor.execute("SELECT event_id, num_tickets FROM bookings WHERE id=?", (booking_id,))
            result = self.cursor.fetchone()
            if result:
                event_id, num_tickets = result['event_id'], result['num_tickets']
                self.cursor.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
                self.cursor.execute("UPDATE events SET available_tickets=available_tickets+? WHERE id=?", (num_tickets, event_id))
                self.conn.commit()
                return "Booking canceled successfully."
        return "Invalid booking ID."

    def show_events(self):
        with self.semaphore:  # Acquire the semaphore before executing the critical section
            self.cursor.execute("SELECT name, date, available_tickets FROM events WHERE date >= ?", (str(date.today()),))
            events = self.cursor.fetchall()
            event_list = "\n".join([f"{row['name']} ({row['date']}) - {row['available_tickets']} available" for row in events])
        return event_list or "No upcoming events."

def handle_client(client_socket, ticket_system):
    user_id = None
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
            print(user_id)
            # response = ticket_system.login(email, password)
        elif request[0] == "create_event":
            name = request[1]
            date = request[2]
            available_tickets = int(request[3])
            response = ticket_system.create_event(name, date, available_tickets)
        elif request[0] == "book_ticket":
            event_id = int(request[1])
            num_tickets = int(request[2])
            response = ticket_system.book_ticket(event_id, user_id, num_tickets)
        elif request[0] == "cancel_booking":
            booking_id = int(request[1])
            response = ticket_system.cancel_booking(booking_id)
        elif request[0] == "show_events":
            response = ticket_system.show_events()
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