import lmdb
from struct import *
from ast import literal_eval

# This starts up the lmdb environment and the databases in it
def startupDatabase():
    global env
    env = lmdb.open('GameDatabase', map_size = 1000000, max_dbs=20)
    global staticWorldDB
    staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
    return env
    return staticWorldDB

# This gets the nine (or less) fields around the player
def getPlayerLocation(clientHandler, env, staticWorldDB):
    txn = env.begin(db=staticWorldDB)
    cursor = txn.cursor(db=staticWorldDB)
    playerLocation = clientHandler.location
    updateArea = {}
    xCoord = playerLocation[0] - 1
    yCoord = playerLocation[1] + 1
    for i in range(3):
        for i in range(3):
            isValidField = True
            try:
                key = pack('II', xCoord, yCoord)
                fieldIsThere = cursor.set_key(key)
            except:
                isValidField = False
            if isValidField == True:
                fieldKey = ''
                if yCoord == playerLocation[1] + 1:
                    fieldKey += 'north '
                elif yCoord == playerLocation[1] - 1:
                    fieldKey += 'south '
                if xCoord == playerLocation[0] + 1:
                    fieldKey += 'east'
                elif xCoord == playerLocation[0] - 1:
                    fieldKey += 'west'
                if xCoord == playerLocation[0] and yCoord == playerLocation[1]:
                    fieldKey += 'center'
                if fieldIsThere == True:
                    field = literal_eval(cursor.value().decode())
                    updateArea[fieldKey] = field
            yCoord -= 1
        xCoord += 1
        yCoord = playerLocation[1] + 1
    return updateArea

# This moves the player in the given direction
def movePlayer(clientHandler, direction, env, staticWorldDB):
    playerLocation = clientHandler.location
    txn = env.begin(db=staticWorldDB)
    cursor = txn.cursor(db=staticWorldDB)

    fieldIsThere = False
    if direction == 'north':
        try:
            fieldIsThere = cursor.set_key(pack('II', playerLocation[0], playerLocation[1] + 1))
        except struct.error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[1] += 1
    if direction == 'south':
        try:
            fieldIsThere = cursor.set_key(pack('II', playerLocation[0], playerLocation[1] - 1))
        except struct.error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[1] -= 1
    if direction == 'east':
        try:
            fieldIsThere = cursor.set_key(pack('II', playerLocation[0] + 1, playerLocation[1]))
        except struct.error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[0] += 1
    if direction == 'west':
        try:
            fieldIsThere = cursor.set_key(pack('II', playerLocation[0] - 1, playerLocation[1]))
            print(fieldIsThere)
        except struct.error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[0] -= 1
    if fieldIsThere == True:
        updateArea = getPlayerLocation(clientHandler, env, staticWorldDB)
        return updateArea
    else:
        return 'destination invalid'

