import socket

def send_request(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 9999))
        client_socket.send(request.encode())
        response = client_socket.recv(1024).decode()
        print(response)

def register():
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    send_request(f"register {name} {email} {password}")

def login():
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    response = send_request(f"login {email} {password}")

def create_event():
    name = input("Enter the event name: ")
    date = input("Enter the event date (YYYY-MM-DD): ")
    available_tickets = input("Enter the number of available tickets: ")
    send_request(f"create_event {name} {date} {available_tickets}")

def book_ticket(user_id):
    event_id = input("Enter the event ID: ")
    num_tickets = input("Enter the number of tickets: ")
    send_request(f"book_ticket {event_id} {num_tickets}")

def cancel_booking():
    booking_id = input("Enter the booking ID: ")
    send_request(f"cancel_booking {booking_id}")

def show_events():
    send_request("show_events")

def main():
    user_id = None
    while True:
        choice = input("Enter your choice (register/login/create_event/book_ticket/cancel_booking/show_events/quit): ")
        if choice == "register":
            register()
        elif choice == "login":
            # response, user_id = login()
            response = login()
            # print(response)
        elif choice == "create_event":
            create_event()
        elif choice == "book_ticket":
            book_ticket(user_id)
            # if user_id:
            #     book_ticket(user_id)
            # else:
            #     print("You need to login first.")
        elif choice == "cancel_booking":
            cancel_booking()
        elif choice == "show_events":
            show_events()
        elif choice == "quit":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()