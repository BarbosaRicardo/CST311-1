"""
Names: Ricardo Barbosa, Max Halbert, Lindsey Reynolds and Dan Sedano
Team: 3
Date: 06/09/2020
Title: EC_Client.py
Description: Extra Credit Assignment. This client will establish a TCP connection
to the server. It will then send a message to the server to be relayed to another
client. 
"""
# team 2

from socket import *
# In your command prompt, type in hostname and press enter.
# What comes up is your computer's hostname

serverName = gethostname()
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

sentence = input('Input lowercase sentence:')
clientSocket.send(sentence.encode())

modifiedSentence = clientSocket.recv(1024)
print ('From Server:', modifiedSentence.decode())

clientSocket.close()




"""
Names: Ricardo Barbosa, Max Halbert, Lindsey Reynolds and Dan Sedano
Team: 3
Date: 06/09/2020
Title: EC_Client.py
Description: Extra Credit Assignment. This client will establish a TCP connection
to the server. It will then send a message to the server to be relayed to another
client. 
"""

from socket import *
from threading import Thread
import time

# variables
serverName = 'localhost'
serverPort = 12000
messageSize = 1024
encoding ='utf-8'
connectionOpen = False

# function to receive messages through client socket
def receiveMessage():
    while True:
        message = clientSocket.recv(1024)
        if not message:
            break
        elif message == "Connection closed":
            connectionOpen = False
            break

        print(message.decode())

        #if client wants to quit, then break loop
        # if message == 'bye':
        #     time.sleep(2)
        #     break   

        # try:
        #     message = clientSocket.recv(1024)
        #     print(message.decode())
 
        # except Exception as e:
        #     # print(e)
        #     break

# function to send messages via client socket
def sendMessage(event=None):
    clientSocket.send(str(message).encode('utf-8'))

# run main routine
if __name__ == '__main__':

    #setup client socket to server
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    connectionOpen = True

    #create thread to receive messages via function
    receiveThread = Thread(target=receiveMessage)
    receiveThread.daemon = True
    receiveThread.start()
    
    #loop keyboard input    
    while connectionOpen:
        message = input('')
        sendMessage()
        #if client wants to quit, then break loop
        # if message == 'bye':
        #     time.sleep(2)
        #     break   
    #close connection
    clientSocket.close()