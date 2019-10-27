from socket import socket, AF_INET, SOCK_STREAM, gethostbyname
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

global lookingFor
lookingFor = 254

global commandBuffer
commandBuffer = bytearray(b'')


def splitUp(update):
    global lookingFor
    global commandBuffer
    returnValue = None
    for byte in update:
        if byte == 254 and lookingFor == 254:
            lookingFor = 237
        elif byte == 237 and lookingFor == 237:
            lookingFor = 250
        elif byte == 250 and lookingFor == 250:
            lookingFor = 206
        elif byte == 206 and lookingFor == 206:
            lookingFor = 254
            returnValue = bytes(commandBuffer)
            commandBuffer = bytearray(b'')
        else:
            commandBuffer.append(byte)
    return returnValue


def recvall(sock):
    global clientKey
    bufsize = 10000
    while True:
        packet = sock.recv(bufsize)
        update = splitUp(packet)
        if update is not None:
            return update
        elif not packet:
            return packet


# This tries to make a connection to the server
def connectToServer(host, port, version):
    global client
    global clientKey
    host = gethostbyname(host)
    try:
        client.connect((host, port))
        key = recvall(client)
        if type(key) == bytes:
            clientKey = key
            client.sendall(bytes(version.encode()))
            connectionResult = recvall(client)
            if type(connectionResult) == bytes:
                f = Fernet(clientKey)
                connectionResult = f.decrypt(connectionResult)
                connectionResult = literal_eval(connectionResult.decode())
                if connectionResult == 'version correct':
                    return 'successfull connection'
                else:
                    return 'version invalid'
            if not connectionResult:
                return 'connection failed'
            else:
                return 'connection failed'
        if not key:
            return 'connection failed'
        else:
            return 'connection failed'

    except ConnectionRefusedError:
        return 'connection failed'
    except OSError:
        return 'connection failed'


# This waits for updates from the server
def getUpdatesFromServer(updateQueue):
    global lastReceivedUpdate
    global client
    while True:
        data = recvall(client)
        if not data:
            updateQueue.put('disconnected')
            break
        timestamp = time()
        lastReceivedUpdate = timestamp
        f = Fernet(clientKey)
        data = f.decrypt(data)
        data = literal_eval(data.decode())
        if type(data) == list:
            for update in data:
                updateQueue.put(update)
        elif type(data) == str:
            updateQueue.put(data)


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
