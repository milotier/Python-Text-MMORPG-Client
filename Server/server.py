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
        self.isLoggedIn = True
    
    def connectionMade(self):
        print(self)
        area = Database.getPlayerLocation(self, env, staticWorldDB)
        update = {}
        update['update'] = {'fields': area}
        message = [update, self.key]
        self.transport.write(bytes(repr(message).encode()))
        self.users.append({'ClientHandler': self})
    
    def rawDataReceived(self, command):
        if self.isLoggedIn == True:
            global commandQueue
            f = Fernet(self.key)
            command = f.decrypt(command)
            CommandHandler.commandQueue.put({'command': command, 'ClientHandler': self})
        else:
            pass

    def connectionLost(self, reason):
        print(reason.type)
        print('Connection lost.')
    
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
#env, staticWorldDB = Database.startupDatabase()
global env
global staticWorldDB
env = lmdb.open('GameDatabase', map_size = 1000000, max_dbs=20)
staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))

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

