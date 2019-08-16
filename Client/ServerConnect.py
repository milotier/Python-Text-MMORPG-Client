from socket import *
from ast import literal_eval
from json import *

# Module which handles the connection with the server


# This makes the socket object
global client
client = socket(AF_INET, SOCK_STREAM)

def recvall(sock):
    data = b''
    bufsize = 4096
    while True:
        packet = sock.recv(bufsize)
        data += packet
        if len(packet) < bufsize:
            break
    return data

# This tries to make a connection to the server
def connectToServer(host, port):
    global client
    try:
        client.connect((host, port))
        connectionResult = recvall(client).decode()
        if type(literal_eval(connectionResult)) == dict:
            return literal_eval(connectionResult)
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
        data = recvall(client)
        data = data.decode()
        if data == 'server went down' or not data:
            updateQueue.put('server went down')
        if type(literal_eval(data)) == dict:
            updateQueue.put(literal_eval(data))
    
# This sends the commands inputted by the user to the server
def sendCommandToServer(sendingCommand):
    global client
    commandType = str(type(sendingCommand).__name__)
    command = {commandType: sendingCommand}
    sendingCommand = dumps(command, default=lambda o: o.__dict__, sort_keys=True)
    sendingCommand = bytes(sendingCommand.encode())
    client.sendall(sendingCommand)
