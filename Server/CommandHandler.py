from time import sleep
from Database import movePlayer, getCompleteUpdate
from queue import Queue
from json import loads

# Here a FIFO queue is made
# that makes sure that a command is only performed once
global commandQueue
commandQueue = Queue()

# This is the list of updates that need to sent to the clients
global updateList
updateList = []


# These are the different classes which make up the different commands
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
    def __init__(self,
                 inputVerb,
                 verbCommentFactor,
                 direction,
                 inputDirection,
                 directionCommentFactor):
        super().__init__(verbCommentFactor,
                         inputVerb,
                         [directionCommentFactor])
        self.direction = Direction(direction,
                                   inputDirection,
                                   directionCommentFactor)


# This will make a command object
# based on what type of command the server has received
def makeCommand(command):
    if 'TravelCommand' in command:
        command = command['TravelCommand']
        travelCommand = TravelCommand(
            command['inputVerb'],
            command['verbCommentFactor'],
            command['direction']['direction'],
            command['direction']['inputDirection'],
            command['direction']['directionCommentFactor'])
        return travelCommand


# Function that will repeatedly perform commands received from the clients
# and send updates to these clients
def performCommands(env, staticWorldDB, characterDB, reactor):
    global commandQueue
    global updateList
    mode = 1
    while True:
        while mode == 1:
            sleep(0.05)
            while not commandQueue.empty():
                command = commandQueue.get()
                clientTimestamp = command['command'][1]
                serverTimestamp = command['ClientHandler'].lastSentUpdate
                clientTimestamp += 10
                sendFullUpdate = False
                if abs(serverTimestamp-clientTimestamp) >= 10 and \
                   clientTimestamp != 0.0:
                    sendFullUpdate = True
                command['command'] = loads(command['command'][0])
                if 'str' in command['command']:
                    if command['command']['str'] == 'disconnect':
                        command['ClientHandler'].transport.abortConnection()
                else:
                    command['command'] = makeCommand(command['command'])

                if type(command['command']) == TravelCommand:
                    outcome = movePlayer(
                        command['ClientHandler'],
                        command['command'].direction.direction,
                        env,
                        staticWorldDB,
                        characterDB)
                    if type(outcome) == dict:
                        if not sendFullUpdate:
                            updateList.append({
                                'ClientHandler': command['ClientHandler'],
                                'updates': outcome})

                    elif outcome == 'destination invalid':
                        print('destination invalid')

                if sendFullUpdate:
                    update = getCompleteUpdate(command['ClientHandler'],
                                               env,
                                               staticWorldDB,
                                               characterDB)
                    updateList.append({
                        'ClientHandler': command['ClientHandler'],
                        'updates': update})

            mode = 2

        while mode == 2:
            while len(updateList) > 0:
                update = updateList.pop(0)
                reactor.callFromThread(update['ClientHandler'].sendData,
                                       update['updates'],
                                       'update')
                print('Update sent.')
            mode = 1
