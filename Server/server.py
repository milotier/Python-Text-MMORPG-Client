from threading import Thread
import CommandHandler
import Database
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import lmdb
from ast import literal_eval
from cryptography.fernet import Fernet
from time import time
from socket import gethostname

# The server module (needless to say)

# Here the port and ip of the server are defined
port = 5555
host = gethostname()
#host = '192.168.1.46'


# This is the ClientHandler class (A twisted Protocol)
# One of these is made everytime a new client connects
# Functions are overridden that handle different things
class ClientHandler(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.setRawMode()
        self.key = Fernet.generate_key()
        self.isLoggedIn = False
        self.loggedInAccount = None
        self.lastSentUpdate = 0.0

    def connectionMade(self):
        self.sendData(self.key, 'key')

    def rawDataReceived(self, command):
        f = Fernet(self.key)
        command = f.decrypt(command).decode()
        command = literal_eval(command)
        if self.isLoggedIn:
            global commandQueue
            CommandHandler.commandQueue.put({'command': command,
                                             'ClientHandler': self})
        else:
            if type(command) == list:
                if 'create' not in command:
                    detailsMatch = Database.checkAccountDetails(self,
                                                                command[0],
                                                                command[1],
                                                                env,
                                                                loginDB)
                    if type(detailsMatch) == int:
                        self.otherClientConnected = False
                        if detailsMatch in self.users:
                            self.users[detailsMatch].loggedInAccount = None
                            self.users[detailsMatch].transport.loseConnection()
                            self.otherClientConnected = True
                        self.isLoggedIn = True
                        self.loggedInAccount = detailsMatch
                        self.users[detailsMatch] = self
                        if not self.otherClientConnected:
                            Database.login(self,
                                           env,
                                           characterDB,
                                           characterLocationDB,
                                           CommandHandler.updateDict,
                                           CommandHandler.updateLock)
                        update = Database.getCompleteUpdate(self,
                                                            env,
                                                            staticWorldDB,
                                                            characterDB,
                                                            characterLocationDB,
                                                            itemDB,
                                                            itemLocationDB,
                                                            inventoryDB)
                        update['type'] = 'full update'
                        self.sendData(update, 'update')
                    else:
                        self.sendData('no match found', 'message')

                else:
                    outcome = Database.createAccount(command[0],
                                                     command[1],
                                                     env,
                                                     loginDB,
                                                     characterDB,
                                                     characterLocationDB,
                                                     accountDB,
                                                     inventoryDB)
                    if type(outcome) == int:
                        self.isLoggedIn = True
                        self.loggedInAccount = outcome
                        self.users[outcome] = self
                        Database.login(self,
                                       env,
                                       characterDB,
                                       characterLocationDB,
                                       CommandHandler.updateDict,
                                       CommandHandler.updateLock)
                        update = Database.getCompleteUpdate(self,
                                                            env,
                                                            staticWorldDB,
                                                            characterDB,
                                                            characterLocationDB,
                                                            itemDB,
                                                            itemLocationDB,
                                                            inventoryDB)
                        update['type'] = 'full update'
                        self.sendData(update, 'update')
                    elif type(outcome) == str:
                        self.sendData(outcome, 'message')

    def connectionLost(self, reason):
        if self.loggedInAccount is not None:
            print('Connection lost with account ' + repr(self.loggedInAccount))
            Database.logout(self,
                            env,
                            characterDB,
                            characterLocationDB,
                            CommandHandler.updateDict,
                            CommandHandler.updateLock)
            self.users.pop(self.loggedInAccount)
        self.transport.abortConnection()

    def sendData(self, data, dataType):
        if dataType == 'key':
            deadBeef = b'\xfe\xed\xfa\xce'
            self.transport.write(bytes(data + deadBeef))
        else:
            deadBeef = b'\xfe\xed\xfa\xce'
            f = Fernet(self.key)
            if dataType == 'update':
                timestamp = time()
                self.lastSentUpdate = timestamp
            data = f.encrypt(bytes(repr(data).encode()))
            self.transport.write(data + deadBeef)


# This is the twisted factory that will make new ClientHandlers
class Server(Factory):

    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return ClientHandler(self.users)


server = Server()

# This starts up the lmdb environment
env = lmdb.open('GameDatabase', map_size=1000000, max_dbs=20)
staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
loginDB = env.open_db(bytes('Login'.encode()))
accountDB = env.open_db(bytes('Accounts'.encode()))
characterDB = env.open_db(bytes('Characters'.encode()))
characterLocationDB = env.open_db(bytes('CharacterLocations'.encode()))
itemDB = env.open_db(bytes('Items'.encode()))
itemLocationDB = env.open_db(bytes('ItemLocations'.encode()))
inventoryDB = env.open_db(bytes('Inventories'.encode()))

# This makes threads that will perform the commands
commandPerformingThread1 = Thread(target=CommandHandler.performCommands,
                                  args=(env,
                                        staticWorldDB,
                                        characterDB,
                                        characterLocationDB,
                                        itemDB,
                                        itemLocationDB,
                                        inventoryDB,
                                        reactor,
                                        server.users))
commandPerformingThread1.daemon = True
commandPerformingThread1.start()

commandPerformingThread2 = Thread(target=CommandHandler.performCommands,
                                  args=(env,
                                        staticWorldDB,
                                        characterDB,
                                        characterLocationDB,
                                        itemDB,
                                        itemLocationDB,
                                        inventoryDB,
                                        reactor,
                                        server.users))
commandPerformingThread2.daemon = True
commandPerformingThread2.start()

commandPerformingThread3 = Thread(target=CommandHandler.performCommands,
                                  args=(env,
                                        staticWorldDB,
                                        characterDB,
                                        characterLocationDB,
                                        itemDB,
                                        itemLocationDB,
                                        inventoryDB,
                                        reactor,
                                        server.users))
commandPerformingThread3.daemon = True
commandPerformingThread3.start()

commandPerformingThread4 = Thread(target=CommandHandler.performCommands,
                                  args=(env,
                                        staticWorldDB,
                                        characterDB,
                                        characterLocationDB,
                                        itemDB,
                                        itemLocationDB,
                                        inventoryDB,
                                        reactor,
                                        server.users))
commandPerformingThread4.daemon = True
commandPerformingThread4.start()

# This will run the server on the specified ip and port
# and run the twisted eventloop
reactor.listenTCP(port, server, interface=host)
reactor.run()
