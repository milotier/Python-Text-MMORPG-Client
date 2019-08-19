import lmdb
from struct import *
from ast import literal_eval
from re import *
from passlib.hash import bcrypt

# This starts up the lmdb environment and the databases in it
def startupDatabase():
    env = lmdb.open('GameDatabase', map_size = 1000000, max_dbs=20)
    staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
    accountDB = env.open_db(bytes('Accounts'.encode()))
    return env
    return staticWorldDB
    return accountDB

def checkPasswordStrength(password):
    digits = search(r'\d', password)
    lowerCaseLetters = search(r'[a-z]', password)
    upperCaseLetters = search(r'[A-Z]', password)
    symbols = search(r"\W", password)

    if digits != None and lowerCaseLetters != None and upperCaseLetters != None and symbols != None and len(password) >= 8:
        passwordIsStrongEnough = True
    else:
        passwordIsStrongEnough = False
    return passwordIsStrongEnough

def checkUsername(username, env, accountDB):
    txn = env.begin(db=accountDB, write=True)
    cursor = txn.cursor(db=accountDB)
    usernameExists = False
    try:
        accountID = 0
        accountExists = cursor.set_key(pack('I', accountID))
        if accountExists == True:
            account = {}
            while usernameExists == False or account != None:
                accountID += 1
                account = cursor.get(pack('I', accountID))
                account = literal_eval(account.decode())
                print(account['username'])
                print(username)
                if account['username'] == username:
                    print('t')
                    usernameExists = True
    except:
        pass
    print(usernameExists)
    return usernameExists
    
def createAccount(username, password, env, accountDB):
    hashedPassword = bcrypt.hash(password)
    txn = env.begin(db=accountDB, write=True)
    cursor = txn.cursor(db=accountDB)
    DBIsEmpty = False
    try:
        accountID = pack('I', 0)
        accountExists = cursor.set_key(accountID)
        if accountExists == False:
            DBIsEmpty = True
    except:
        DBIsEmpty = True
    if DBIsEmpty == False:
        cursor.last()
        highestAccountID = cursor.key()
        highestAccountID = int.from_bytes(highestAccountID, byteorder='little')
        accountID = highestAccountID + 1
    else:
        accountID = 0
    print(accountID)
    account = {'username': username, 'password': hashedPassword, 'status': 'OWNER'}
    cursor.put(pack('I', accountID), bytes(repr(account).encode()))
    cursor.close()
    txn.commit()
    return accountID

# This gets the nine (or less) fields around the player
def getPlayerLocation(clientHandler, env, staticWorldDB):
    txn = env.begin(db=staticWorldDB)
    cursor = txn.cursor(db=staticWorldDB)
    playerLocation = clientHandler.location
    updateArea = {}
    xCoord = playerLocation[0] - 1
    yCoord = playerLocation[1] + 1
    zCoord = playerLocation[2]
    for i in range(3):
        for i in range(3):
            isValidField = True
            try:
                key = pack('III', xCoord, yCoord, zCoord)
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
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0], playerLocation[1] + 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[1] += 1
    elif direction == 'south':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0], playerLocation[1] - 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[1] -= 1
    elif direction == 'east':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] + 1, playerLocation[1], playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[0] += 1
    elif direction == 'west':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] - 1, playerLocation[1], playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[0] -= 1
    elif direction == 'north-east':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] + 1, playerLocation[1] + 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[0] += 1
            clientHandler.location[1] += 1
    elif direction == 'north-west':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] - 1, playerLocation[1] + 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[0] -= 1
            clientHandler.location[1] += 1
    elif direction == 'south-east':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] + 1, playerLocation[1] - 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[0] += 1
            clientHandler.location[1] -= 1
    elif direction == 'south-west':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] - 1, playerLocation[1] - 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            clientHandler.location[0] -= 1
            clientHandler.location[1] -= 1
    if fieldIsThere == True:
        updateArea = getPlayerLocation(clientHandler, env, staticWorldDB)
        return updateArea
    else:
        return 'destination invalid'

