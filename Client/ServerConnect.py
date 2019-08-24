from socket import socket, AF_INET, SOCK_STREAM
from ast import literal_eval
from json import dumps
from cryptography.fernet import Fernet

# Module which handles the connection with the server


# This makes the socket object
global client
client = socket(AF_INET, SOCK_STREAM)

global clientKey
clientKey = ''


def recvall(sock):
    global clientKey
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
        connectionResult = recvall(client)
        if type(connectionResult) == bytes:
            clientKey = connectionResult
            return 'successfull connection'
        if not connectionResult:
            return 'connection failed'
        else:
            return 'connection failed'

    except ConnectionRefusedError:
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
# TODO: Add timestamps of last received update from server to command
def sendCommandToServer(sendingCommand):
    global client
    commandType = str(type(sendingCommand).__name__)
    command = {commandType: sendingCommand}
    sendingCommand = bytes(dumps(command,
                           default=lambda o: o.__dict__,
                           sort_keys=True).encode())
    f = Fernet(clientKey)
    sendingCommand = f.encrypt(bytes(repr(sendingCommand).encode()))
    client.sendall(sendingCommand)


def loginToAccount(accountDetails):
    global client
    f = Fernet(clientKey)
    accountDetails = f.encrypt(bytes(repr(accountDetails).encode()))
    client.sendall(accountDetails)
    client.sendall(accountDetails)
    loginOutcome = recvall(client)
    loginOutcome = f.decrypt(loginOutcome)
    loginOutcome = literal_eval(loginOutcome.decode())
    return loginOutcome


def createAccount(accountDetails):
    global client
    f = Fernet(clientKey)
    accountDetails.append('create')
    accountDetails = f.encrypt(bytes(repr(accountDetails).encode()))
    client.sendall(accountDetails)
    creationOutcome = recvall(client)
    creationOutcome = f.decrypt(creationOutcome)
    creationOutcome = literal_eval(creationOutcome.decode())
    return creationOutcome
