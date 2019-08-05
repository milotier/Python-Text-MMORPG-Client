from threading import *
import socket
from queue import *
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.application.internet import TCPServer
from twisted.internet import reactor


port = 5555
host = '127.0.0.1'

commandQueue = Queue()

def testWrite(command, client):
    encodedCommand = str.encode(command)
    client.transport.write(bytes(encodedCommand))
    print('sent: ' + command)
    

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

class Server(Factory):

    def __init__(self):
        self.users = [] 

    def buildProtocol(self, addr):
        return ClientHandler(self.users)

server = Server()


reactor.listenTCP(port, server, interface=host)
reactor.run()
for user in server.users:
    user['ClientHandler'].transport.write(bytes('server went down'.encode()))
print(server.users)



