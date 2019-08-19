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
        self.location = [0, 0, 5]
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
                    self.isLoggedIn = True
                    area = Database.getPlayerLocation(self, env, staticWorldDB)
                    update = {}
                    update['update'] = {'fields': area}
                    self.sendData(update)
                    message = [update, self.key]
                else:
                    passwordIsStrongEnough = Database.checkPasswordStrength(command[1])
                    usernameAlreadyExists = Database.checkUsername(command[0], env, accountDB)
                    if passwordIsStrongEnough == True and usernameAlreadyExists == False:
                        accountID = Database.createAccount(command[0], command[1], env, accountDB)
                        self.isLoggedIn = True
                        self.loggedInAccount = accountID
                        area = Database.getPlayerLocation(self, env, staticWorldDB)
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
global accountDB
env = lmdb.open('GameDatabase', map_size = 1000000, max_dbs=20)
staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
accountDB = env.open_db(bytes('Accounts'.encode()))
characterDB = env.open_db(bytes('Characters'.encode()))

# This makes threads that will perform the commands
commandPerformingThread1 = Thread(target=CommandHandler.performCommands, args=(env, staticWorldDB, reactor))
commandPerformingThread1.daemon = True
commandPerformingThread1.start()
commandPerformingThread2 = Thread(target=CommandHandler.performCommands, args=(env, staticWorldDB, reactor))
commandPerformingThread2.daemon = True
commandPerformingThread2.start()
commandPerformingThread3 = Thread(target=CommandHandler.performCommands, args=(env, staticWorldDB, reactor))
commandPerformingThread3.daemon = True
commandPerformingThread3.start()
commandPerformingThread4 = Thread(target=CommandHandler.performCommands, args=(env, staticWorldDB, reactor))
commandPerformingThread4.daemon = True
commandPerformingThread4.start()

# This will run the server on the specified ip and port and run the twisted eventloop
reactor.listenTCP(port, server, interface=host)

reactor.run()

