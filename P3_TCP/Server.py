# Names: Ricardo Barbosa, Max Halbert, Lindsey Reynolds and Dan Sedano
# Team: 3
# Date: 06/09/2020
# Title: Server.py
# Description: This is a TCP Server program that will connect to two different
# clients simultaneously. The server will receive one message from each server 
# and will process each message. The server will then send the messages back to
# the correct client.

from socket import *
from threading import *
from time import *

# ****************** Team, lets keep these links here for future reference :) ******************
# # This video talks about multithreaded servers https://www.youtube.com/watch?v=pPOBH21RnaA
# # From Max: https://www.techbeamers.com/python-tutorial-write-multithreaded-python-server/


# Define global variables
message_count = 0 # Count messages arriving at server
first_client = "" # Store name of first client to connect

# Define mutex variables 
message_count_lock = Lock() # Lock for the message_count variable
message_cv = Condition(message_count_lock) # A CV to wait for server to receive both messages 


# Creates a class for each client thread
class ClientConnection(Thread):  
    # Constructor 
    def __init__(self, ip, port, connection, client_id): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port
        self.connection = connection
        self.client_name = ""
        self.ack_message = ""
        # Assigns client names to thread and sets ack_message message
        if (client_id == 1):
            print ("Accepted first connection, calling it client X")
            self.client_name = "X"
            self.ack_message = "Client X connected"
        else:
            print("Accepted second connection, calling it client Y")
            self.client_name = "Y"
            self.ack_message = "Client Y connected"
    
    # sets the message rcvd counter
    def set_message_counter(self):
        global message_cv
        global message_count
        message_cv.acquire()  # acquire the lock to update message counter
                
        # If this is the first message
        if (message_count == 0):
            message_count = message_count + 1 
        else:
            message_count = message_count + 1
        message_cv.notify()   # to notify the main thread a message is received
        message_cv.release()  # release the lock

    # Returns the acknowledgment message
    def get_ack_message(self):
        return self.ack_message
    # Returns the client's name
    def get_client_name(self):
        return self.client_name
    # Sends clients an acknowledgment message, allowing client to send message back
    def send_ack_message(self):
        self.connection.send(self.get_ack_message().encode())
    # Returns broadcast message
    def get_server_broadcast(self):
        #self.server_broadcast = f"Client {self.client_name}: {self.client_message}"
        self.server_broadcast = "Client " + self.client_name + ": " + self.client_message 
        return self.server_broadcast
    #Sends a message to client
    def send_message(self,message):
        self.connection.send(message.encode())

    def received_from_client(self):
        print("Client ", self.client_name, " sent message ", message_count, ": ", self.client_message)

    def set_first_client(self):
        global first_client
        # store client_id of the client that returned the first message
        if message_count == 1:
            first_client = self.client_name


    def run(self):
        self.client_message = ""
        global message_count
        while True:
            self.client_message = self.connection.recv(1024).decode()
            if not self.client_message:
                # client connection closed
                break
            else:
                self.set_message_counter()
                self.set_first_client()
                self.received_from_client()
        self.connection.close()    # close the connection and this thread is done


# --------------------------------------- End of Class --------------------------------------- #

# Broadcasts the order of message received to all clients
def create_broadcast_msg(connections,first_client):
    if first_client == "X":
        #constructs broadcast message
        broadcast_message = f"{connections[0].get_server_broadcast()} before {connections[1].get_server_broadcast()}"
    else:
        broadcast_message = f"{connections[1].get_server_broadcast()} before {connections[0].get_server_broadcast()}"
    return broadcast_message

# broadcasts ack to clients
def send_broadcast_ack(connections, broadcast_message):
    for c in connections:
        c.send_message(broadcast_message)


# Main method
def main():
    # Multithreaded Python server : TCP Server Socket Program Stub
    SERVER_PORT = 12000 
    BUFFER_SIZE = 1024  # Usually 1024, but we need quick response 

    serverSocket = socket(AF_INET, SOCK_STREAM)  
    serverSocket.bind(('', SERVER_PORT)) 
    # Holds the connection threads
    connections = []

    # using 2 as a parameter to allow for 2 connections to be queued
    serverSocket.listen(2)      
    print ("The server is ready to receive two connections...\n")
    client_id = 1 # used to identify the client

    while True: 
        (connectionSocket, (ip,port)) = serverSocket.accept() 
        new_connection = ClientConnection(ip,port,connectionSocket,client_id) 
        new_connection.start() 
        connections.append(new_connection)
        client_id = client_id + 1

        # Checks that there is more than one client before finalizing the connection
        if(len(connections) > 1):
            for c in connections:
                c.send_ack_message()
            break
    # wait for both connections to receive a message
    print("\nWaiting to receive messages from client X and client Y....\n")
    
    message_cv.acquire()
    while (message_count != 2):
        message_cv.wait() # wait for a thread's notification for any message received
    # broadcasts an ack to all clients
    broadcast_message = create_broadcast_msg(connections,first_client)
    send_broadcast_ack(connections,broadcast_message)

    print("\nWaiting a bit for clients to close connections")

    for c in connections: 
        c.join()

    print("Done.")

# ------------------------------- Run Main ---------------------------------- #
if __name__ == "__main__":
    main()