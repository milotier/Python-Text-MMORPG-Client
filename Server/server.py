from threading import *
import socket
import CommandHandler
import Database
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.application.internet import TCPServer
from twisted.internet import reactor
import lmdb
from time import sleep
from ast import literal_eval
from cryptography.fernet import Fernet

# The server module (needless to say)

# Here the port and ip of the server are defined
port = 5555
host = ''

    
# This is the ClientHandler class (A twisted Protocol). One of these is made everytime a new client connects
# Functions are overridden that handle different things 
class ClientHandler(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.setRawMode()
        self.key = Fernet.generate_key()
        self.isLoggedIn = False
        self.loggedInAccount = None
    
    def connectionMade(self):
        self.transport.write(self.key)
        self.users.append({'ClientHandler': self})
    
    def rawDataReceived(self, command):
        f = Fernet(self.key)
        command = f.decrypt(command).decode()
        command = literal_eval(command)
        if self.isLoggedIn == True:
            global commandQueue
            CommandHandler.commandQueue.put({'command': command, 'ClientHandler': self})
        else:
            if type(command) == list:
                if not 'create' in command:
                    detailsMatch = Database.checkAccountDetails(self, command[0], command[1], env, loginDB)
                    if type(detailsMatch) == int:
                        self.isLoggedIn = True
                        self.loggedInAccount = detailsMatch
                        area = Database.getPlayerArea(self, env, staticWorldDB, characterDB)
                        update = {}
                        update['update'] = {'fields': area}
                        self.sendData(update)
                    # TODO: Send message to client if account details don't match
                    else:
                        pass

                else:
                    passwordIsStrongEnough = Database.checkPasswordStrength(command[1])
                    usernameAlreadyExists = Database.checkUsername(command[0], env, loginDB)
                    print(passwordIsStrongEnough)
                    print(usernameAlreadyExists)
                    if passwordIsStrongEnough == True and usernameAlreadyExists == False:
                        accountID = Database.createAccount(command[0], command[1], env, loginDB, characterDB, accountDB)
                        self.isLoggedIn = True
                        self.loggedInAccount = accountID
                        area = Database.getPlayerArea(self, env, staticWorldDB, characterDB)
                        update = {}
                        update['update'] = {'fields': area}
                        self.sendData(update)
                    else:
                        if passwordIsStrongEnough == False:
                            self.sendData('password too weak')
                        elif usernameAlreadyExists == True:
                            self.sendData('username already exists')

    def connectionLost(self, reason):
        print('Connection lost.')
        self.transport.abortConnection()
    
    # TODO: Add current time to message
    def sendData(self, data):
        f = Fernet(self.key)
        data = f.encrypt(bytes(repr(data).encode()))
        self.transport.write(data)

# This is the twisted factory that will make new CientHandlers
class Server(Factory):

    def __init__(self):
        self.users = [] 

    def buildProtocol(self, addr):
        return ClientHandler(self.users)

server = Server()

# This starts up the lmdb environment
global env
global staticWorldDB
global loginDB
env = lmdb.open('GameDatabase', map_size = 1000000, max_dbs=20)
staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
loginDB = env.open_db(bytes('Login'.encode()))
accountDB = env.open_db(bytes('Accounts'.encode()))
characterDB = env.open_db(bytes('Characters'.encode()))

# This makes threads that will perform the commands
commandPerformingThread1 = Thread(target=CommandHandler.performCommands, args=(env, staticWorldDB, characterDB, reactor))
commandPerformingThread1.daemon = True
commandPerformingThread1.start()
commandPerformingThread2 = Thread(target=CommandHandler.performCommands, args=(env, staticWorldDB, characterDB, reactor))
commandPerformingThread2.daemon = True
commandPerformingThread2.start()
commandPerformingThread3 = Thread(target=CommandHandler.performCommands, args=(env, staticWorldDB, characterDB, reactor))
commandPerformingThread3.daemon = True
commandPerformingThread3.start()
commandPerformingThread4 = Thread(target=CommandHandler.performCommands, args=(env, staticWorldDB, characterDB, reactor))
commandPerformingThread4.daemon = True
commandPerformingThread4.start()

# This will run the server on the specified ip and port and run the twisted eventloop
reactor.listenTCP(port, server, interface=host)

reactor.run()

