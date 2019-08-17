from socket import *
from ast import literal_eval
from json import *
from cryptography.fernet import Fernet

# Module which handles the connection with the server


# This makes the socket object
global client
client = socket(AF_INET, SOCK_STREAM)

global clientKey 
clientKey = ''

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
    global clientKey
    try:
        client.connect((host, port))
        connectionResult = literal_eval(recvall(client).decode())
        if type(connectionResult) == list:
            clientKey = connectionResult[1]
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
        data = recvall(client)
        if not data:
            updateQueue.put('server went down')
            break
        f = Fernet(clientKey)
        data = f.decrypt(data)
        if type(literal_eval(data.decode())) == dict:
            updateQueue.put(literal_eval(data.decode()))
    
# This sends the commands inputted by the user to the server
def sendCommandToServer(sendingCommand):
    global client
    commandType = str(type(sendingCommand).__name__)
    command = {commandType: sendingCommand}
    sendingCommand = bytes(dumps(command, default=lambda o: o.__dict__, sort_keys=True).encode())
    f = Fernet(clientKey)
    sendingCommand = f.encrypt(sendingCommand)
    client.sendall(sendingCommand)
