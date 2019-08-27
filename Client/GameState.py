from queue import Queue
from time import sleep

# The module which saves the game state and updates it
# TODO: Save more types of data in the GameState module:
# Player status, inventory, amount of players in current area, etc

# This defines the function of every of the four major output windows
# and the text they should contain
global playerInfoWindowText
global commandOutputWindowText
global inventoryWindowText
global chatWindowText
global outputArea1Function
global outputArea2Function
global outputArea3Function
global outputArea4Function

# TODO: Add more functions the output windows can have
outputArea1Function = 'inventoryWindow'
outputArea2Function = 'skillWindow'
outputArea3Function = 'commandOutputWindow'
outputArea4Function = 'chatWindow'
inventoryWindowText = ''
skillWindowText = ''
commandOutputWindowText = ''
chatWindowText = ''

global area
area = {}
global playerLocation
playerLocation = {}

# This defines the queue object
# that will order the different updates of the screen as FIFO (FirstInFirstOut)
screenUpdateQueue = Queue()


# This updates the game state
def updateState(updates, app):
    global skillWindowText
    global commandOutputWindowText
    global inventoryWindowText
    global chatWindowText
    global outputArea1Function
    global outputArea2Function
    global outputArea3Function
    global outputArea4Function
    global area
    global playerLocation
    if updates == 'server went down':
        app.exit()
        sleep(0.5)
        print('\n\nThe server is down at the moment.', end=' ')
        print('Please wait and come back later.\n\n')

    if type(updates) == list:
        for change in updates:
            if change[0] == 'outputArea1Function':
                if change[1] == 'skillWindow':
                    outputArea1Function = 'skillWindow'
                if change[1] == 'commandOutputWindow':
                    outputArea1Function = 'commandOutputWindow'
                if change[1] == 'inventoryWindow':
                    outputArea1Function = 'inventoryWindow'
                if change[1] == 'chatWindow':
                    outputArea1Function = 'chatWindow'
            elif change[0] == 'outputArea2Function':
                if change[1] == 'skillWindow':
                    outputArea2Function = 'skillWindow'
                if change[1] == 'commandOutputWindow':
                    outputArea2Function = 'commandOutputWindow'
                if change[1] == 'inventoryWindow':
                    outputArea2Function = 'inventoryWindow'
                if change[1] == 'chatWindow':
                    outputArea2Function = 'chatWindow'
            elif change[0] == 'outputArea3Function':
                if change[1] == 'skillWindow':
                    outputArea3Function = 'skillWindow'
                if change[1] == 'commandOutputWindow':
                    outputArea3Function = 'commandOutputWindow'
                if change[1] == 'inventoryWindow':
                    outputArea3Function = 'inventoryWindow'
                if change[1] == 'chatWindow':
                    outputArea3Function = 'chatWindow'
            elif change[0] == 'outputArea4Function':
                if change[1] == 'skillWindow':
                    outputArea4Function = 'skillWindow'
                if change[1] == 'commandOutputWindow':
                    outputArea4Function = 'commandOutputWindow'
                if change[1] == 'inventoryWindow':
                    outputArea4Function = 'inventoryWindow'
                if change[1] == 'chatWindow':
                    outputArea4Function = 'chatWindow'
    elif type(updates) == dict:
        if 'fields' in updates:
            if 'update' in updates['fields']:
                for update in updates['fields']['update']:
                    area[update] = updates['fields']['update'][update]
            if 'remove' in updates['fields']:
                for removal in updates['fields']['remove']:
                    area.pop(removal, None)
        if 'characterLocation' in updates:
            playerLocation = area[updates['characterLocation']]

    outputArea4Function = 'chatWindow'
    # chatWindowText = repr(area)
