from threading import *
import socket
from queue import *
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.application.internet import TCPServer
from twisted.internet import reactor

# The server module (needless to say)

# Here the port and ip of the server are defined
port = 5555
host = '127.0.0.1'

# Here a FIFO queue is made that makes sure that a command is only performed once
commandQueue = Queue()

# Just function to test sending info back to a certain client
def testWrite(command, client):
    encodedCommand = str.encode(command)
    client.transport.write(bytes(encodedCommand))
    print('sent: ' + command)
    
# This is the ClientHandler class (A twisted Protocol). One of these is made everytime a new client connects
# It overrides funcions that handle different things 
class ClientHandler(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.setRawMode()
    
    def connectionMade(self):
        print(self)
        self.transport.write(bytes('succesfull connection'.encode()))
        self.users.append({'ClientHandler': self})
    
    def rawDataReceived(self, command):
        command = command.decode()
        print('received: ' + command)
        if command == 'disconnect':
            self.transport.abortConnection()
        

    def connectionLost(self, reason):
        print(reason.type)
        print('Connection lost.')

# This is the twisted factory that will make new CientHandlers
class Server(Factory):

    def __init__(self):
        self.users = [] 

    def buildProtocol(self, addr):
        return ClientHandler(self.users)

server = Server()

# This will run the server on the specified ip and port and run the twisted eventloop
reactor.listenTCP(port, server, interface=host)
reactor.run()
# This will run when ctrl-c is pressed and send a signal to every client telling them the server went down
for user in server.users:
    user['ClientHandler'].transport.write(bytes('server went down'.encode()))
