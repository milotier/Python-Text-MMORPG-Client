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
global areaDescriptionWindowText
global outputArea1Function
global outputArea2Function
global outputArea3Function
global outputArea4Function

# TODO: Add more functions the output windows can have
outputArea1Function = 'inventoryWindow'
outputArea2Function = 'areaDescriptionWindow'
outputArea3Function = 'commandOutputWindow'
outputArea4Function = 'chatWindow'
inventoryWindowText = ''
skillWindowText = ''
commandOutputWindowText = ''
chatWindowText = ''
areaDescriptionWindowText = ''

global area
area = {}
global playerLocation
playerLocation = {}
global itemLocations
itemLocations = {}

# This defines the queue object
# that will order the different updates of the screen as FIFO (FirstInFirstOut)
screenUpdateQueue = Queue()


# This updates the game state
def updateState(updates, app):
    global skillWindowText
    global commandOutputWindowText
    global inventoryWindowText
    global chatWindowText
    global areaDescriptionWindowText
    global outputArea1Function
    global outputArea2Function
    global outputArea3Function
    global outputArea4Function
    global area
    global playerLocation
    global itemLocations
    if updates == 'server went down':
        app.exit()
        sleep(0.5)
        print('\n\nThe server is down at the moment.', end=' ')
        print('Please wait and come back later.\n\n')

    elif updates['type'] == 'update':
        if 'itemLocations' in updates:
            if 'remove' in updates['itemLocations']:
                for removal in updates['itemLocations']['remove']:
                    itemLocations.pop(removal, None)
            if 'update' in updates['itemLocations']:
                for update in updates['itemLocations']['update']:
                    itemLocations[update] = updates['itemLocations']['update'][update]

        if 'staticFields' in updates:
            if 'remove' in updates['staticFields']:
                for removal in updates['staticFields']['remove']:
                    area.pop(removal, None)
            if 'update' in updates['staticFields']:
                for update in updates['staticFields']['update']:
                    area[update] = updates['staticFields']['update'][update]


        if 'characterLocation' in updates:
            playerLocation = area[updates['characterLocation']]

        if 'staticFields' in updates or 'itemLocations' in updates:
            areaDescriptionWindowText = ''
            characterLocationString = ''
            for field in area:
                if area[field] == playerLocation:
                    characterLocationString = field
            characterLocation = characterLocationString.split(' ')
            characterLocation = list(map(int, characterLocation))
            for field in area:
                if field == characterLocationString:
                    areaDescriptionWindowText += area[field]['description'] + '\n\n'

            for field in itemLocations:
                if field == characterLocationString:
                    itemNames = []
                    for item in itemLocations[field]:
                        itemNames.append(item['name'])
                    iteration = 0
                    for itemName in itemNames:
                        if iteration == 0 and len(itemNames) == 1:
                            areaDescriptionWindowText += 'There is a ' + itemName + ' lying on the ground.\n\n'
                            break
                        elif iteration == 0 and len(itemNames) > 1:
                            areaDescriptionWindowText += 'There is a ' + itemName
                        elif iteration != 0 and iteration + 1 != len(itemNames):
                            areaDescriptionWindowText += ', ' + itemName
                        elif iteration != 0 and iteration + 1 == len(itemNames):
                            areaDescriptionWindowText += ' and ' + itemName + ' lying on the ground.\n\n'

                        iteration += 1
            
            for field in area:
                if field != characterLocationString:
                    fieldLocation = field.split(' ')
                    fieldLocation = list(map(int, fieldLocation))
                    if characterLocation[1] < fieldLocation[1] and \
                       fieldLocation[0] == characterLocation[0] and \
                       fieldLocation[2] == fieldLocation[2]:
                        areaDescriptionWindowText += 'To the north you see ' + \
                                                    area[field]['summary'] + \
                                                    '\n'

            for field in area:
                if field != characterLocationString:
                    fieldLocation = field.split(' ')
                    fieldLocation = list(map(int, fieldLocation))
                    if characterLocation[1] > fieldLocation[1] and \
                       fieldLocation[0] == characterLocation[0] and \
                       fieldLocation[2] == fieldLocation[2]:
                        areaDescriptionWindowText += 'To the south you see ' + \
                                                    area[field]['summary'] + \
                                                    '\n'
            for field in area:
                if field != characterLocationString:
                    fieldLocation = field.split(' ')
                    fieldLocation = list(map(int, fieldLocation))
                    if characterLocation[0] < fieldLocation[0] and \
                       fieldLocation[1] == characterLocation[1] and \
                       fieldLocation[2] == fieldLocation[2]:
                        areaDescriptionWindowText += 'To the east you see ' + \
                                                    area[field]['summary'] + \
                                                    '\n'
            for field in area:
                if field != characterLocationString:
                    fieldLocation = field.split(' ')
                    fieldLocation = list(map(int, fieldLocation))
                    if characterLocation[0] > fieldLocation[0] and \
                       fieldLocation[1] == characterLocation[1] and \
                       fieldLocation[2] == fieldLocation[2]:
                        areaDescriptionWindowText += 'To the west you see ' + \
                                                    area[field]['summary'] + \
                                                    '\n'
            for field in area:
                if field != characterLocationString:
                    fieldLocation = field.split(' ')
                    fieldLocation = list(map(int, fieldLocation))
                    if characterLocation[1] < fieldLocation[1] and \
                       fieldLocation[0] > characterLocation[0] and \
                       fieldLocation[2] == fieldLocation[2]:
                        areaDescriptionWindowText += 'To the northeast you see ' + \
                                                    area[field]['summary'] + \
                                                    '\n'
            for field in area:
                if field != characterLocationString:
                    fieldLocation = field.split(' ')
                    fieldLocation = list(map(int, fieldLocation))
                    if characterLocation[1] < fieldLocation[1] and \
                       fieldLocation[0] < characterLocation[0] and \
                       fieldLocation[2] == fieldLocation[2]:
                        areaDescriptionWindowText += 'To the northwest you see ' + \
                                                    area[field]['summary'] + \
                                                    '\n'
            for field in area:
                if field != characterLocationString:
                    fieldLocation = field.split(' ')
                    fieldLocation = list(map(int, fieldLocation))
                    if characterLocation[1] > fieldLocation[1] and \
                       fieldLocation[0] > characterLocation[0] and \
                       fieldLocation[2] == fieldLocation[2]:
                        areaDescriptionWindowText += 'To the southeast you see ' + \
                                                    area[field]['summary'] + \
                                                    '\n'
            for field in area:
                if field != characterLocationString:
                    fieldLocation = field.split(' ')
                    fieldLocation = list(map(int, fieldLocation))
                    if characterLocation[1] > fieldLocation[1] and \
                       fieldLocation[0] < characterLocation[0] and \
                       fieldLocation[2] == fieldLocation[2]:
                        areaDescriptionWindowText += 'To the southwest you see ' + \
                                                    area[field]['summary'] + \
                                                    '\n'

    elif updates['type'] == 'full update':
        area = {}
        playerLocation = {}
        for update in updates['staticFields']['update']:
            area[update] = updates['staticFields']['update'][update]
        areaDescriptionWindowText = ''
        for field in area:
            if field == updates['characterLocation']:
                areaDescriptionWindowText += area[field]['description'] + '\n\n'
        itemLocations = {}
        for update in updates['itemLocations']['update']:
            itemLocations[update] = updates['itemLocations']['update'][update]
        for field in itemLocations:
            if field == updates['characterLocation']:
                itemNames = []
                for item in itemLocations[field]:
                    itemNames.append(item['name'])
                iteration = 0
                for itemName in itemNames:
                    if iteration == 0 and len(itemNames) == 1:
                        areaDescriptionWindowText += 'There is a ' + itemName + ' lying on the ground.\n\n'
                        break
                    elif iteration == 0 and len(itemNames) > 1:
                        areaDescriptionWindowText += 'There is a ' + itemName
                    elif iteration != 0 and iteration + 1 != len(itemNames):
                        areaDescriptionWindowText += ', ' + itemName
                    elif iteration != 0 and iteration + 1 == len(itemNames):
                        areaDescriptionWindowText += ' and ' + itemName + ' lying on the ground.\n\n'

                    iteration += 1
        characterLocation = updates['characterLocation'].split(' ')
        characterLocation = list(map(int, characterLocation))
        for field in area:
            if field != updates['characterLocation']:
                fieldLocation = field.split(' ')
                fieldLocation = list(map(int, fieldLocation))
                if characterLocation[1] < fieldLocation[1] and \
                   fieldLocation[0] == characterLocation[0] and \
                   fieldLocation[2] == fieldLocation[2]:
                    areaDescriptionWindowText += 'To the north you see ' + \
                                                area[field]['summary'] + \
                                                '\n'

        for field in area:
            if field != updates['characterLocation']:
                fieldLocation = field.split(' ')
                fieldLocation = list(map(int, fieldLocation))
                if characterLocation[1] > fieldLocation[1] and \
                   fieldLocation[0] == characterLocation[0] and \
                   fieldLocation[2] == fieldLocation[2]:
                    areaDescriptionWindowText += 'To the south you see ' + \
                                                area[field]['summary'] + \
                                                '\n'
        for field in area:
            if field != updates['characterLocation']:
                fieldLocation = field.split(' ')
                fieldLocation = list(map(int, fieldLocation))
                if characterLocation[0] < fieldLocation[0] and \
                   fieldLocation[1] == characterLocation[1] and \
                   fieldLocation[2] == fieldLocation[2]:
                    areaDescriptionWindowText += 'To the east you see ' + \
                                                area[field]['summary'] + \
                                                '\n'
        for field in area:
            if field != updates['characterLocation']:
                fieldLocation = field.split(' ')
                fieldLocation = list(map(int, fieldLocation))
                if characterLocation[0] > fieldLocation[0] and \
                   fieldLocation[1] == characterLocation[1] and \
                   fieldLocation[2] == fieldLocation[2]:
                    areaDescriptionWindowText += 'To the west you see ' + \
                                                area[field]['summary'] + \
                                                '\n'
        for field in area:
            if field != updates['characterLocation']:
                fieldLocation = field.split(' ')
                fieldLocation = list(map(int, fieldLocation))
                if characterLocation[1] < fieldLocation[1] and \
                   fieldLocation[0] > characterLocation[0] and \
                   fieldLocation[2] == fieldLocation[2]:
                    areaDescriptionWindowText += 'To the northeast you see ' + \
                                                area[field]['summary'] + \
                                                '\n'
        for field in area:
            if field != updates['characterLocation']:
                fieldLocation = field.split(' ')
                fieldLocation = list(map(int, fieldLocation))
                if characterLocation[1] < fieldLocation[1] and \
                   fieldLocation[0] < characterLocation[0] and \
                   fieldLocation[2] == fieldLocation[2]:
                    areaDescriptionWindowText += 'To the northwest you see ' + \
                                                area[field]['summary'] + \
                                                '\n'
        for field in area:
            if field != updates['characterLocation']:
                fieldLocation = field.split(' ')
                fieldLocation = list(map(int, fieldLocation))
                if characterLocation[1] > fieldLocation[1] and \
                   fieldLocation[0] > characterLocation[0] and \
                   fieldLocation[2] == fieldLocation[2]:
                    areaDescriptionWindowText += 'To the southeast you see ' + \
                                                area[field]['summary'] + \
                                                '\n'
        for field in area:
            if field != updates['characterLocation']:
                fieldLocation = field.split(' ')
                fieldLocation = list(map(int, fieldLocation))
                if characterLocation[1] > fieldLocation[1] and \
                   fieldLocation[0] < characterLocation[0] and \
                   fieldLocation[2] == fieldLocation[2]:
                    areaDescriptionWindowText += 'To the southwest you see ' + \
                                                area[field]['summary'] + \
                                                '\n'
        playerLocation = area[updates['characterLocation']]
