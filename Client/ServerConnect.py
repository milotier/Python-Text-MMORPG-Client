from socket import *
from time import sleep


global client
client = socket(AF_INET, SOCK_STREAM)

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

def getUpdatesFromServer(updateQueue):
    global client
    while True:
        receivedUpdate = client.recv(10000).decode()

        if not receivedUpdate or receivedUpdate == 'server went down':
            updateQueue.put('server went down')

def sendCommandToServer(sendingCommand):
    sendingCommand = sendingCommand.encode()
    client.sendall(bytes(sendingCommand))
