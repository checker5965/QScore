# ===================== Imports ========================


import os
import socket
import hashlib
import smtplib
import ssl
import getpass
import threading
from random import randint


# ======================================================


# ======================= Globals ======================


EMAIL = input("Enter E-mail to send OTPs from: ")
PASSWORD = getpass.getpass("Enter Password: ")


# ======================================================


# ===================== Helper Functions ========================


# Helpfer function to get IP
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

# Helper function to send OTPs
def sendMail(otp, receiver, sender = EMAIL, password = PASSWORD):
    port = 465
    smtp_server = "smtp.gmail.com"
    name = receiver.partition(".")[0].title() 
    text = "Hi {}!\n\nYour OTP is: {}".format(name, otp)
    subject = "Your OTP"
    message = 'Subject: {}\n\n{}'.format(subject, text)
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context = context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, message)
    print("OTP Sent Successfully!")
    return


# Helper function to create grades hashmap from csv file
def constructGrades(filename):
    dictionary = {}
    f = open(filename, "r")
    header = f.readline().strip("\n").split(",")
    for line in f:
        temp = line.strip("\n").split(",")
        dictionary[temp[0]] = []
        for element in range(1, len(temp)):
            dictionary[temp[0]].append(str(temp[element]))
    f.close()
    return (dictionary, header)


# Helper function to create a hashmap from csv file
def constructDict(filename):
    dictionary = {}
    f = open(filename, "r")
    for line in f:
        temp = line.strip("\n").split(",")
        dictionary[temp[0]] = str(temp[1])
    f.close()
    return dictionary


# Helper function to save a key-value pair to a csv file
def saveDetails(filename, key, value):
    f = open(filename, "a")
    f.write(str(key) + "," + str(value) + "\n")
    f.close()


# ================================================================


# ===================== Setting things up ========================


IP = get_ip_address()
PORT = 8728

# create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to IP address, and a port
serversocket.bind((IP, PORT))

# become a server socket
serversocket.listen(128)
print("Server is running! (IP address - %s, Port - %s)" % (IP, PORT))


# grades.csv contains email-address followed by grade
grades = constructGrades("grades.csv")
header = grades[1]
grades = grades[0]

# login.csv contains email-address followed by a hash of the password
login = constructDict("login.csv")


# ==================================================================


# ======================== Running the Server ======================


# Main Function
def checkingThread(clientsocket):
    
    # recv data from client
    data = clientsocket.recv(1024).decode()
    
    # Check if student is registered for the course
    if data not in grades:
        print("1: Student not registered.")
        clientsocket.send("1".encode())
        clientsocket.close()

    # Student is registered
    else:
        # Check if the student has an account
        if data in login:
            print("2: Accepting password now.")

            # Request for password
            clientsocket.send("2".encode())
            secret = clientsocket.recv(1024).decode()

            # Hash the password
            salt = bytes.fromhex(login[data][:64])
            key = hashlib.pbkdf2_hmac('sha256', secret.encode('utf-8'), salt, 100000).hex()
            secret = 0
            
            # Send grade if hash matches, else exit
            if login[data][64:] == key:
                grade = grades[data]
                toSend = header[1] + " = " + grade[0]
                for i in range(2, len(header)):
                    toSend += ", " + header[i] + " = " + grade[i-1]
                print("Grade sent!")                
                clientsocket.send(toSend.encode())
            else:
                print("3: Incorrect password.")
                clientsocket.send("3".encode())
        
        # If student does not have an account, ask if they want to register
        else:
            print("4: User Unregistered.")
            clientsocket.send("4".encode())
            answer = clientsocket.recv(1024).decode()
            
            # If user wants to create an account
            if answer == "y":
                
                print("5: Creating new account.")
                
                # Ask them for password, password confirmation, and OTP
                clientsocket.send("5".encode())
                secret1 = clientsocket.recv(1024).decode()
                clientsocket.send("6".encode())
                secret2 = clientsocket.recv(1024).decode()
                clientsocket.send("7".encode())
                OTP = randint(100000,999999)
                sendMail(OTP, data)
                secret_otp = clientsocket.recv(1024).decode()

                # Hash the passwords
                salt = os.urandom(32)
                key1 = hashlib.pbkdf2_hmac('sha256', secret1.encode('utf-8'), salt, 100000).hex()
                key2 = hashlib.pbkdf2_hmac('sha256', secret2.encode('utf-8'), salt, 100000).hex()
                secret1, secret2 = 0, 0
                
                # If the hashes match, create account
                if key1 == key2 and secret_otp == str(OTP):
                    print("8: Account Created Successfully!")
                    clientsocket.send("8".encode())
                    login[data] = salt.hex() + key1

                    # Save user id and password hash to login.csv
                    saveDetails("login.csv", data, salt.hex() + key1)
                
                # re-attempt if passwords don't match
                elif secret_otp == OTP:
                    print("9: Passwords don't match.")
                    clientsocket.send("9".encode())
                
                else:
                    print("10: Wrong OTP Entered.")
                    clientsocket.send("10".encode())
    
    # Close the connection
    print("Closing connection.")
    clientsocket.close()

# Server running
while True:
    
    # accept connections from outside
    (clientsocket, address) = serversocket.accept()
    print("Got a connection from ", address)

    # Create a thread and start it
    t1 = threading.Thread(target = checkingThread, args = (clientsocket, ))
    t1.start()