from socket import *
from time import sleep

# Module which handles the connection with the server

# This makes the socket object
global client
client = socket(AF_INET, SOCK_STREAM)

# This tries to make a connection to the server
def connectToServer(host, port):
    global client
    try:
        client.connect((host, port))
        connectionResult = client.recv(2048).decode()
        if connectionResult == 'succesfull connection':
            return connectionResult
        if not connectionResult:
            return 'connection failed'
        else:
            return 'connection failed'

    except:
        return 'connection failed'

# This waits for updates from the server
def getUpdatesFromServer(updateQueue):
    global client
    while True:
        receivedUpdate = client.recv(10000).decode()

        if not receivedUpdate or receivedUpdate == 'server went down':
            updateQueue.put('server went down')

# This sends the commands inputted by the user to the server
def sendCommandToServer(sendingCommand):
    sendingCommand = sendingCommand.encode()
    client.sendall(bytes(sendingCommand))
