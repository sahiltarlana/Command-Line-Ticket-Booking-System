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
    send_request(f"login {email} {password}")

while True:
    choice = input("Are you a new user? (y/n) ")
    if choice.lower() == "y":
        register()
    elif choice.lower() == "n":
        login()
    else:
        print("Invalid input. Please try again.")