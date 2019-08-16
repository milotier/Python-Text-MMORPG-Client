from time import sleep
from Database import *
from queue import *
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory, Protocol
from json import *
from collections import namedtuple
from jsonpickle import *

# Here a FIFO queue is made that makes sure that a command is only performed once
global commandQueue
commandQueue = Queue()

global updateList
updateList = []

class Direction:
    def __init__(self, direction, inputDirection, directionCommentFactor):
        self.direction = direction
        self.inputDirection = inputDirection
        self.directionCommentFactor = directionCommentFactor

class Command:
    def __init__(self, verbCommentFactor, inputVerb, commentFactorList):
        self.inputVerb = inputVerb
        self.verbCommentFactor = verbCommentFactor
        self.commentFactor = self.verbCommentFactor
        commentFactorNum = 0
        commentFactorNum = 1
        for commentFactor in commentFactorList:
            self.commentFactor += commentFactor
            commentFactorNum += 1
        self.commentFactor = commentFactor / commentFactorNum


class TravelCommand(Command):
    def __init__(self, inputVerb, verbCommentFactor, direction, inputDirection, directionCommentFactor):
        super().__init__(verbCommentFactor, inputVerb, [directionCommentFactor])
        self.direction = Direction(direction, inputDirection, directionCommentFactor)

def makeCommand(command):
    if 'TravelCommand' in command:
        command = command['TravelCommand']
        travelCommand = TravelCommand(command['inputVerb'], command['verbCommentFactor'], command['direction']['direction'], command['direction']['inputDirection'], command['direction']['directionCommentFactor'])
        return travelCommand


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
                command['command'] = loads(command['command'])
                print(command['command'])
                if command['command'] == 'disconnect':
                    command['ClientHandler'].transport.abortConnection()
                else:
                    command['command'] = makeCommand(command['command'])
                if type(command['command']) == TravelCommand:
                    outcome = movePlayer(command['ClientHandler'], command['command'].direction.direction, env, staticWorldDB)
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