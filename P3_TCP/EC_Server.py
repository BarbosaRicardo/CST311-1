"""
Names: Ricardo Barbosa, Max Halbert, Lindsey Reynolds and Dan Sedano
Team: 3
Date: 06/09/2020
Title: EC_Server.py
Description: Extra Credit Assignment. This server will act as the processing 
relay between to clients. That is, this server will receive two connections
from two different clients. Each client will then send a message to the other 
client via the server. Example Client X wants to send  message to Client Y. To
do so it has to go through the server first (X -> S -> Y)
"""

from socket import *
from threading import *
from time import *

# ****************** Team, lets keep these links here for future reference :) ******************
# # This video talks about multithreaded servers https://www.youtube.com/watch?v=pPOBH21RnaA
# # From Max: https://www.techbeamers.com/python-tutorial-write-multithreaded-python-server/


# Define global variables
first_client = "" # Store name of first client to connect
connections = []

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

    # Returns the acknowledgment message
    def get_ack_message(self):
        return self.ack_message

    # Sends clients an acknowledgment message, allowing client to send message back
    def send_ack_message(self):
        self.connection.send(self.get_ack_message().encode())

    #Sends a message to client
    def send_message(self,message):
        self.connection.send(message.encode())

    def run(self):
        self.client_message = ""
        while True:
            self.client_message = self.connection.recv(1024).decode()
            if not self.client_message:
                break
            if self.client_message.lower() == "bye":
                for thread in connections:
                    thread.send_message("Connection closed")
                break
                
            for thread in connections:
                thread.send_message(self.client_message)

        self.connection.close()    # close the connection and this thread is done


# --------------------------------------- End of Class --------------------------------------- #

# Main method
def main():
    # Multithreaded Python server : TCP Server Socket Program Stub
    SERVER_PORT = 12000 
    BUFFER_SIZE = 1024  # Usually 1024, but we need quick response 

    serverSocket = socket(AF_INET, SOCK_STREAM)  
    serverSocket.bind(('', SERVER_PORT)) 
    # Holds the connection threads
    global connections

    # using 2 as a parameter to allow for 2 connections to be queued
    serverSocket.listen(2)      
    print ("The server is ready to receive two connections...\n")
    client_id = 1 # used to identify the client

    # Accept arriving connections
    while True: 
        (connectionSocket, (ip,port)) = serverSocket.accept() 
        new_connection = ClientConnection(ip,port,connectionSocket,client_id) 
        new_connection.daemon = True
        new_connection.start() 
        connections.append(new_connection)
        client_id = client_id + 1

        # Checks that there is more than one client before finalizing the connection
        if(len(connections) > 1):
            for c in connections:
                c.send_ack_message()
            break

    print("\nClients are chatting")

    for c in connections: 
        c.join()

    print("Done.")

# ------------------------------- Run Main ---------------------------------- #
if __name__ == "__main__":
    main()