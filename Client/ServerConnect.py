from socket import socket, AF_INET, SOCK_STREAM
from ast import literal_eval
from json import dumps
from cryptography.fernet import Fernet
from sys import exit
from time import time

# Module which handles the connection with the server


# This makes the socket object
global client
client = socket(AF_INET, SOCK_STREAM)

global clientKey
clientKey = ''

global lastReceivedUpdate
lastReceivedUpdate = 0.0


def recvall(sock):
    global clientKey
    data = b''
    bufsize = 10000
    while True:
        packet = sock.recv(bufsize)
        data += packet
        if data[-4:] == b'\xfe\xed\xfa\xce':
            break
    return data[0:-4]


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
    global lastReceivedUpdate
    global client
    while True:
        data = recvall(client)
        if not data:
            updateQueue.put('server went down')
            break
        print(data)
        timestamp = time()
        lastReceivedUpdate = timestamp
        f = Fernet(clientKey)
        data = f.decrypt(data)
        data = literal_eval(data.decode())
        if type(data) == list:
            for update in data:
                updateQueue.put(update)
                print(update)


# This sends the commands inputted by the user to the server
def sendCommandToServer(sendingCommand):
    global client
    global lastReceivedUpdate
    commandType = str(type(sendingCommand).__name__)
    command = {commandType: sendingCommand}
    sendingCommand = bytes(dumps(command,
                           default=lambda o: o.__dict__,
                           sort_keys=True).encode())
    f = Fernet(clientKey)
    sendingCommand = [sendingCommand, lastReceivedUpdate]
    sendingCommand = f.encrypt(bytes(repr(sendingCommand).encode()))
    client.sendall(sendingCommand)


def loginToAccount(accountDetails):
    global client
    f = Fernet(clientKey)
    accountDetails = f.encrypt(bytes(repr(accountDetails).encode()))
    client.sendall(accountDetails)
    client.sendall(accountDetails)
    loginOutcome = recvall(client)
    if not loginOutcome:
        print('\n\nThe server is down at the moment.', end=' ')
        print('Please wait and come back later.\n\n')
        exit()
    loginOutcome = f.decrypt(loginOutcome)
    loginOutcome = literal_eval(loginOutcome.decode())
    return loginOutcome


def createAccount(accountDetails):
    global client
    print(clientKey)
    f = Fernet(clientKey)
    accountDetails.append('create')
    accountDetails = f.encrypt(bytes(repr(accountDetails).encode()))
    client.sendall(accountDetails)
    creationOutcome = recvall(client)
    if not creationOutcome:
        print('\n\nThe server is down at the moment.', end=' ')
        print('Please wait and come back later.\n\n')
        exit()
    creationOutcome = f.decrypt(creationOutcome)
    creationOutcome = literal_eval(creationOutcome.decode())
    return creationOutcome
