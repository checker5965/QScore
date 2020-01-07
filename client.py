# ===================== Imports ======================


import socket
import getpass


# ====================================================

# ===================== Setting Things up ======================


email = input("Enter your E-mail ID: ")


# ==============================================================


# ===================== Main Function ======================


def checkGrade(email): 
    # Connect to the client
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(("10.1.45.98", 8728))
    
    # Send E-mail ID
    clientsocket.send(email.encode())
    response = clientsocket.recv(1024).decode() 
    
    # If server responds with 1, this E-mail address is not registered for the class
    if response[0] == "1":
        print("You are not registered for the class.")

    # If server responds with 2, this E-mail address is registered for the class, and has an account
    elif response[0] == "2":

        # Enter password
        secret = getpass.getpass("Enter your Password: ")
        clientsocket.send(secret.encode())
        response = clientsocket.recv(1024).decode() 
        
        # If password is incorrect, give the user the option to try again
        if response[0] == "3":
            print("Incorrect password.")
            user_input = input("Try again?\nEnter y/n: ")
            if user_input == "y":
                clientsocket.close()
                checkGrade(email)
                return
        
        # If password is correct, print the grade that the server sends
        else:
            print("Your latest score is: " + response)
    
    # If server responds with 1, this E-mail address is registered for the class, but does not have an account    
    elif response[0] == "4":

        # Give the user the option to create an account
        print("Unregistered User. Create new account?") 
        user_input = input("Enter y/n: ")

        # If user wants to create account
        if user_input == "y":
            clientsocket.send("y".encode())

            # Enter and confirm password
            response = clientsocket.recv(1024).decode()
            secret = getpass.getpass("Create your password: ")
            clientsocket.send(secret.encode())
            response = clientsocket.recv(1024).decode()
            secret = getpass.getpass("Enter your password again: ")
            clientsocket.send(secret.encode())
            response = clientsocket.recv(1024).decode()
            secret = getpass.getpass("Enter OTP sent to your E-mail: ")
            clientsocket.send(secret.encode())
            response = clientsocket.recv(1024).decode()
            
            # If all goes well and passwords match, account will be successfully created 
            # Send another request to check grade
            if response[0] == "8":
                print("Account successfully created!")
                clientsocket.close()
                checkGrade(email)
                return
            
            # If passwords don't match, give the user the option to try again
            elif response[0] == "9":
                print("Your passwords didn't match!")
                user_input = input("Try again?\nEnter y/n: ")
                if user_input == "y":
                    clientsocket.close()
                    checkGrade(email)
                    return
            
            elif response[:2] == "10":
                print("Your OTP is incorrect!")
                user_input = input("Try again?\nEnter y/n: ")
                if user_input == "y":
                    clientsocket.close()
                    checkGrade(email)
                    return
        
        else:
            clientsocket.send("n".encode())

    # Exit
    print("Exiting.")
    clientsocket.close()
    return


checkGrade(email)