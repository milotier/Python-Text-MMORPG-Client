import lmdb
from struct import *

def startupDatabase():
    global env
    env = lmdb.open('GameDatabase', map_size = 1000000, max_dbs=20)
    global staticWorldDB
    staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
    return env
    return staticWorldDB

def movePlayer(clientHandler, direction, env, staticWorldDB):
    playerLocation = clientHandler.location
    txn = env.begin(db=staticWorldDB)
    cursor = txn.cursor(db=staticWorldDB)
    if direction == 'north':
        fieldIsThere = cursor.set_key(pack('II', playerLocation[0], playerLocation[1] + 1))
        if fieldIsThere == True:
            clientHandler.location[1] += 1
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
                        if fieldIsThere == True:
                            field = cursor.value()
                            updateArea[key] = field
                    yCoord -= 1
                xCoord += 1
                yCoord = playerLocation[1] + 1
            return updateArea
        else:
            return 'destination invalid'

