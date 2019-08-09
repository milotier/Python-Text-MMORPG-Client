from time import sleep
from Database import *
from queue import *
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory, Protocol

# Here a FIFO queue is made that makes sure that a command is only performed once
global commandQueue
commandQueue = Queue()


global updateList
updateList = []

# Function that will repeatedly perform commands received from the clients and send updates to these clients
def performCommands(env, staticWorldDB, reactor):
    global commandQueue
    global updateList
    mode = 1
    while True:
        while mode == 1:
            sleep(0.05)
            while commandQueue.empty() == False:
                command = commandQueue.get()
                if command['command'] == 'disconnect':
                    command['ClientHandler'].transport.abortConnection()
                elif command['command'] == 'go north':
                    outcome = movePlayer(command['ClientHandler'], 'north', env, staticWorldDB)
                    if type(outcome) == dict:
                        print(command['ClientHandler'].location)
                        updateList.append({'ClientHandler': command['ClientHandler'], 'updates': {'update': {'fields': outcome}}})

                    elif outcome == 'destination invalid':
                        print('destination invalid')
            mode = 2

        while mode == 2:
            while len(updateList) > 0:
                update = updateList.pop(0)
                reactor.callFromThread(update['ClientHandler'].transport.write, bytes(repr(update['updates']).encode()))
                print('Update sent.')
            mode = 1