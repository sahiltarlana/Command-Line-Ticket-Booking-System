import socket

def send_request(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 9999))
        client_socket.send(request.encode())
        response = client_socket.recv(1024).decode()
        print(response)
        
def login():
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    response = send_request(f"login {email} {password}")
    
def create_bus():
    name = input("Enter the bus name: ")
    date = input("Enter the bus date (YYYY-MM-DD): ")
    available_tickets = input("Enter the number of available tickets: ")
    send_request(f"create_bus {name} {date} {available_tickets}")
    
def show_bus():
    send_request("show_bus")
    
def main():
    user_id = None
    while True:
        choice = input("Enter your choice (login/create_bus/show_bus/quit): ")
        if choice == "login":
            login()
        elif choice == "create_bus":
            create_bus()
        elif choice == "show_bus":
            show_bus()
        elif choice == "quit":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()