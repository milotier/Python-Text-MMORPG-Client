from time import sleep
from Database import movePlayer, \
                     takeItem, \
                     dropItem, \
                     getCompleteUpdate
from queue import Queue
from threading import Lock
from json import loads

# Here a FIFO queue is made
# that makes sure that a command is only performed once
global commandQueue
commandQueue = Queue()

# This is the list of updates that need to be sent to the clients
global updateDict
updateDict = {}
global updateLock
updateLock = Lock()


# These are the different classes which make up the different commands
class Direction:
    def __init__(self, direction, inputDirection, directionCommentFactor):
        self.direction = direction
        self.inputDirection = inputDirection
        self.directionCommentFactor = directionCommentFactor


class Item:
    def __init__(self,
                 itemName):
        self.itemName = itemName


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
        self.commentFactor = self.commentFactor / commentFactorNum


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


class TakeCommand(Command):
    def __init__(self,
                 inputVerb,
                 verbCommentFactor,
                 itemName):
        super().__init__(verbCommentFactor,
                         inputVerb,
                         [])
        self.targetItem = Item(itemName)


class DropCommand(Command):
    def __init__(self,
                 inputVerb,
                 verbCommentFactor,
                 itemName):
        super().__init__(verbCommentFactor,
                         inputVerb,
                         [])
        self.targetItem = Item(itemName)


# This will make a command object
# based on what type of command the server has received
def makeCommand(command):
    if 'TravelCommand' in command:
        command = command['TravelCommand']
        command = TravelCommand(
            command['inputVerb'],
            command['verbCommentFactor'],
            command['direction']['direction'],
            command['direction']['inputDirection'],
            command['direction']['directionCommentFactor'])
    elif 'TakeCommand' in command:
        command = command['TakeCommand']
        command = TakeCommand(
            command['inputVerb'],
            command['verbCommentFactor'],
            command['targetItem']['itemName'])
    elif 'DropCommand' in command:
        command = command['DropCommand']
        command = DropCommand(
            command['inputVerb'],
            command['verbCommentFactor'],
            command['targetItem']['itemName'])
    return command


# Function that will repeatedly perform commands received from the clients
# and send updates to these clients
def performCommands(env,
                    staticWorldDB,
                    characterDB,
                    characterLocationDB,
                    itemDB,
                    itemLocationDB,
                    inventoryDB,
                    reactor,
                    users):
    global commandQueue
    global updateDict
    global updateLock
    mode = 1
    while True:
        while mode == 1:
            sleep(0.05)
            while not commandQueue.empty():
                command = commandQueue.get()
                clientTimestamp = command['command'][1]
                serverTimestamp = command['ClientHandler'].lastSentUpdate
                sendFullUpdate = False
                if abs(serverTimestamp-clientTimestamp) >= 10 and \
                   clientTimestamp != 0.0:
                    sendFullUpdate = True
                sendFullUpdate = True
                command['command'] = loads(command['command'][0])
                disconnected = False
                if 'str' in command['command']:
                    if command['command']['str'] == 'disconnect':
                        command['ClientHandler'].transport.abortConnection()
                        disconnected = True
                else:
                    command['command'] = makeCommand(command['command'])

                if type(command['command']) == TravelCommand:
                    outcome = movePlayer(
                        command['ClientHandler'],
                        command['command'].direction.direction,
                        env,
                        staticWorldDB,
                        characterDB,
                        characterLocationDB,
                        itemDB,
                        itemLocationDB)
                    if type(outcome) == dict and not sendFullUpdate:
                        with updateLock:
                            for item in outcome:
                                if type(item) == int:
                                    outcome[item]['type'] = 'update'
                                    if item not in updateDict:
                                        updateDict[item] = []
                                        updateDict[item].append(outcome[item])
                                    else:
                                        updateDict[item].append(outcome[item])

                    elif outcome == 'destination invalid':
                        print('destination invalid')

                if type(command['command']) == TakeCommand:
                    outcome = takeItem(
                        command['ClientHandler'],
                        command['command'].targetItem,
                        env,
                        inventoryDB,
                        itemLocationDB,
                        itemDB,
                        characterDB,
                        characterLocationDB)
                    if type(outcome) == dict and not sendFullUpdate:
                        with updateLock:
                            for item in outcome:
                                if type(item) == int:
                                    outcome[item]['type'] = 'update'
                                    if item not in updateDict:
                                        updateDict[item] = []
                                        updateDict[item].append(outcome[item])
                                    else:
                                        updateDict[item].append(outcome[item])
                    elif outcome == 'item nonexisting':
                        print('item doesn\'t exist.')

                if type(command['command']) == DropCommand:
                    outcome = dropItem(
                        command['ClientHandler'],
                        command['command'].targetItem,
                        env,
                        inventoryDB,
                        itemLocationDB,
                        itemDB,
                        characterDB,
                        characterLocationDB)
                    if type(outcome) == dict and not sendFullUpdate:
                        with updateLock:
                            for item in outcome:
                                if type(item) == int:
                                    outcome[item]['type'] = 'update'
                                    if item not in updateDict:
                                        updateDict[item] = []
                                        updateDict[item].append(outcome[item])
                                    else:
                                        updateDict[item].append(outcome[item])
                    elif outcome == 'item nonexisting':
                        print('item doesn\'t exist.')

                if not disconnected:
                    if sendFullUpdate and type(outcome) == dict:
                        updates = {}
                        update = getCompleteUpdate(command['ClientHandler'],
                                                   env,
                                                   staticWorldDB,
                                                   characterDB,
                                                   itemDB,
                                                   itemLocationDB,
                                                   inventoryDB)
                        with updateLock:
                            for item in outcome:
                                if type(item) == int:
                                    if item == command['ClientHandler'].loggedInAccount:
                                        outcome[item] = update
                                        outcome[item]['type'] = 'full update'
                                        if item not in updateDict:
                                            updateDict[item] = []
                                            updateDict[item].append(outcome[item])
                                        else:
                                            updateDict[item].append(outcome[item])
                                    else:
                                        outcome[item]['type'] = 'update'
                                        if item not in updateDict:
                                            updateDict[item] = []
                                            updateDict[item].append(outcome[item])
                                        else:
                                            updateDict[item].append(outcome[item])
                        print(updates)

            mode = 2

        while mode == 2:
            while len(updateDict) > 0:
                with updateLock:
                    try:
                        account = next(iter(updateDict))
                        updates = updateDict.pop(account)
                    except StopIteration:
                        account = None
                if account is not None:
                    if account in users:
                        reactor.callFromThread(users[account].sendData,
                                               updates,
                                               'update')
                        print('Update sent to account ' + repr(account))
            mode = 1
