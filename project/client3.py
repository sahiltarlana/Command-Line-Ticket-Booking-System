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

def book_ticket():
    user_id = input("Enter your user ID: ")
    bus_id = input("Enter the bus ID: ")
    num_tickets = input("Enter the number of tickets: ")
    send_request(f"book_ticket {user_id} {bus_id} {num_tickets}")

def cancel_booking():
    booking_id = input("Enter the booking ID: ")
    send_request(f"cancel_booking {booking_id}")

def show_bus():
    send_request("show_bus")

def main():
    cnt=0
    choice = input("Are you a new user? (y/n) ")
    while True :
        if choice.lower() == "y":
            register()
            choice = "n"
        elif choice.lower() == "n":
            response = login()
            cnt=1
            break
        else:
            print("Invalid input. Please try again.")
    while(cnt==1):
        show_bus()
        print("\tTicket Booking System\n")
        print ("what you want to do :")
        print ("if you wnat to book ticket , press 1 ")
        print ("if you want to cancel booking, press 2 ")
        print ("if you want to exit ,press 0 ")
        choice =input("chioce : ")
        if choice == "1":
            book_ticket()
        elif choice == "2":
            cancel_booking()
        elif choice == "0":
            break
        else :
            print("Invalid choice .Please try again.")

if __name__ == "__main__":
    main()