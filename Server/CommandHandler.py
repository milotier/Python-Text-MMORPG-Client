from time import sleep
from Database import movePlayer, \
                     takeItem, \
                     dropItem, \
                     getCompleteUpdate
from queue import Queue
from json import loads

# Here a FIFO queue is made
# that makes sure that a command is only performed once
global commandQueue
commandQueue = Queue()

# This is the list of updates that need to be sent to the clients
global updateList
updateList = []


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
    global updateList
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
                command['command'] = loads(command['command'][0])
                print(command['command'])
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
                        characterDB,
                        characterLocationDB,
                        itemDB,
                        itemLocationDB)
                    if type(outcome) == dict:
                        if not sendFullUpdate:
                            for item in outcome:
                                if type(item) == int:
                                    outcome[item]['type'] = 'update'
                            updateList.append({
                                'ClientHandler': command['ClientHandler'],
                                'updates': outcome})

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
                    if type(outcome) == dict:
                        if not sendFullUpdate:
                            for item in outcome:
                                if type(item) == int:
                                    outcome[item]['type'] = 'update'
                            updateList.append({
                                'ClientHandler': command['ClientHandler'],
                                'updates': outcome})
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
                    if type(outcome) == dict:
                        if not sendFullUpdate:
                            for item in outcome:
                                if type(item) == int:
                                    outcome[item]['type'] = 'update'
                            updateList.append({
                                'ClientHandler': command['ClientHandler'],
                                'updates': outcome})
                    elif outcome == 'item nonexisting':
                        print('item doesn\'t exist.')

                if sendFullUpdate and type(outcome) == dict:
                    update = getCompleteUpdate(command['ClientHandler'],
                                               env,
                                               staticWorldDB,
                                               characterDB,
                                               itemDB,
                                               itemLocationDB,
                                               inventoryDB)
                    update['type'] = 'full update'
                    updateList.append({
                        'ClientHandler': command['ClientHandler'],
                        'updates': update})

            mode = 2

        while mode == 2:
            while len(updateList) > 0:
                updates = updateList.pop(0)
                for update in updates['updates']:
                    if type(update) == int:
                        client = users[update]
                        reactor.callFromThread(client.sendData,
                                               updates['updates'][update],
                                               'update')
                        print('Update sent to account ' + repr(update))
            mode = 1
