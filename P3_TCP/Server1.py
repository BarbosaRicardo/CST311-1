# Names: Ricardo Barbosa, Max Halbert, Lindsey Reynolds and Dan Sedano
# Team: 3
# Date: 06/09/2020
# Title: Server.py
# Description: This is a TCP Server program will will connect to two different
# clients simultaneously. The server will receive one message from each server 
# and will process each message. The server will then send the messages back to
# the correct client.

from socket import *
from threading import *
from time import *


# # This video talks about multithreaded servers https://www.youtube.com/watch?v=pPOBH21RnaA
# # From Max: https://www.techbeamers.com/python-tutorial-write-multithreaded-python-server/


# Counter for counting messages arrived to server
msgCtr = 0
# Message to be sent to all clients
msg = ""
# A lock to protect the msgCtr update
msgCtr_lock = Lock()
# A condition variable to wait for message received by both client threads
cvToSend = Condition(msgCtr_lock)

first_client = ""

class ClientThread(Thread):  
    # constructor 
    def __init__(self,ip,port,conn,clientID): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port
        self.conn = conn
        self.clientName = ""
        self.handshake = ""
        self.timestamp = 0.0
        if (clientID == 1):
            print ("Accepted first connection, calling it client X")
            self.clientName = "X"
            self.handshake = "Client X connected"
        else:
            print("Accepted second connection, calling it client Y")
            self.clientName = "Y"
            self.handshake = "Client Y connected"
        #self.conn.send(self.handshake.encode())

    def run(self):
        global msgCtr #not sure if this is "kosher"
        self.server_output = ""
        self.client_message = ""
        global first_client
        # self.cvToSend = Condition(Lock())
        while True:
            self.client_message = self.conn.recv(1024).decode()
            if not self.client_message:
                # client connection closed
                break
            else:
                cvToSend.acquire()  # acquire the lock to update message counter
                
                if (msgCtr == 0):   # it is the first message
                    self.server_output = self.clientName + ": " + self.client_message + " received before "
                    msgCtr = msgCtr + 1 
                    # store clientID of the client that returned the first message
                    first_client = self.clientName
                    
                else:               # it is the second message
                    self.server_output = self.server_output + self.clientName + ": " + self.client_message
                    msgCtr = msgCtr + 1
                print("Client ", self.clientName, " sent message ", msgCtr, ": ", self.client_message)
                
                cvToSend.notify()   # to notify the main thread a message is received
                cvToSend.release()  # release the lock
               
        self.conn.close()    # close the connection and this thread is done

    def get_connections(self):
        return self.conn
    
    def get_handshake(self):
        return self.handshake
    
    def get_client_name(self):
        return self.clientName
    
    # Sends clients a handshake messaging allowing client to send message back
    def send_handshake(self):
        self.conn.send(self.get_handshake().encode())

    def get_msg(self):
        return self.server_output

    def send_message(self,message):
        print("before send")
        print(message)
        self.conn.send(message.encode())
        print("after send")

# Multithreaded Python server : TCP Server Socket Program Stub
SERVER_IP = gethostname() # server hostname 
SERVER_PORT = 12000 
BUFFER_SIZE = 1024  # Usually 1024, but we need quick response 

serverSocket = socket(AF_INET, SOCK_STREAM)  
# tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
serverSocket.bind(('', SERVER_PORT)) 
threads = []

# using 2 as a parameter to allow for 2 connections to be queued
serverSocket.listen(2)      
print ("The server is ready to receive two connections...")
clientID = 1

while True: 
    (connectionSocket, (ip,port)) = serverSocket.accept() 
    newthread = ClientThread(ip,port,connectionSocket,clientID) 
    newthread.start() 
    threads.append(newthread)
    clientID = clientID + 1

    if(len(threads) % 2 == 0):
        for t in threads:
            t.send_handshake()
        break

# wait for both threads to receive a message
cvToSend.acquire()
while (msgCtr != 2):
    cvToSend.wait()     # wait for a thread's notification for any message received

# message is ready to send to all the clients
print(f"ClientName: {first_client}") #tracer
if first_client == "X":
    print("Yes") # tracer
    for t in threads:
        print("in the loop") # tracer
        message = "Client X: First message received before Client Y"
        t.send_message(message)
        print(f"message to {t} sent {message}") # tracer
else:
    for t in threads:
        message = "Client Y: First message received before Client X"
        t.send_message(message)

print("Waiting a bit for clients to close connections")

for t in threads: 
    t.join()
print("Done.")