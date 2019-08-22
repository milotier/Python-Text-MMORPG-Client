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

def checkUsername(username, env, loginDB):
    txn = env.begin(db=loginDB, write=True)
    cursor = txn.cursor(db=loginDB)
    print(username)
    username = cursor.get(bytes(username.encode()))
    print(username)
    if username == None:
        usernameExists = False
    else:
        usernameExists = True
    return usernameExists
    
def createAccount(username, password, env, loginDB, characterDB, accountDB):
    print(password)
    hashedPassword = bcrypt.hash(password)
    txn = env.begin(db=accountDB, write=True)
    cursor = txn.cursor(db=accountDB)
    DBIsEmpty = False
    currentID = 0
    accountID = None
    while accountID == None:
        accountExists = cursor.set_key(pack('I', currentID))
        if accountExists == False:
            accountID = currentID
        else:
            currentID += 1

    print(accountID)
    cursor.put(pack('I', accountID), bytes(repr({'username': username, 'status': 'Owner'}).encode()))
    cursor.close()
    txn.commit()
    txn = env.begin(db=loginDB, write=True)
    cursor = txn.cursor(db=loginDB)
    account = {'ID': accountID, 'password': hashedPassword}
    cursor.put(bytes(username.encode()), bytes(repr(account).encode()))
    cursor.close()
    txn.commit()
    txn = env.begin(db=characterDB, write=True)
    cursor = txn.cursor(db=characterDB)
    character = {'location': [1, 1, 5]}
    cursor.put(pack('I', accountID), bytes(repr(character).encode()))
    cursor.close()
    txn.commit()
    return accountID

def checkAccountDetails(clientHandler, username, password, env, loginDB):
    txn = env.begin(db=loginDB)
    cursor = txn.cursor(db=loginDB)
    detailsMatch = False
    account = cursor.get(bytes(username.encode()))
    account = literal_eval(account.decode())
    if account != None:
        passwordsMatch = bcrypt.verify(password, account['password'])
        if passwordsMatch == True:
            detailsMatch = account['ID']
        else:
            detailsMatch = False
    else:
        detailsMatch = False
    return detailsMatch

def getPlayerLocation(clientHandler, env, characterDB):
    txn = env.begin(db=characterDB)
    cursor = txn.cursor(db=characterDB)
    accountID = clientHandler.loggedInAccount
    character = cursor.get(pack('I', accountID))
    character = literal_eval(character.decode())
    playerLocation = character['location']
    return playerLocation

# This gets the nine (or less) fields around the player
def getPlayerArea(clientHandler, env, staticWorldDB, characterDB):
    playerLocation = getPlayerLocation(clientHandler, env, characterDB)
    updateArea = {}
    xCoord = playerLocation[0] - 1
    yCoord = playerLocation[1] + 1
    zCoord = playerLocation[2]
    txn = env.begin(db=staticWorldDB)
    cursor = txn.cursor(db=staticWorldDB)
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
def movePlayer(clientHandler, direction, env, staticWorldDB, characterDB):
    playerLocation = getPlayerLocation(clientHandler, env, characterDB)
    txn = env.begin(db=staticWorldDB)
    cursor = txn.cursor(db=staticWorldDB)
    fieldIsThere = False
    if direction == 'north':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0], playerLocation[1] + 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            playerLocation[1] += 1
    elif direction == 'south':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0], playerLocation[1] - 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            playerLocation[1] -= 1
    elif direction == 'east':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] + 1, playerLocation[1], playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            playerLocation[0] += 1
    elif direction == 'west':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] - 1, playerLocation[1], playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            playerLocation[0] -= 1
    elif direction == 'north-east':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] + 1, playerLocation[1] + 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            playerLocation[0] += 1
            playerLocation[1] += 1
    elif direction == 'north-west':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] - 1, playerLocation[1] + 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            playerLocation[0] -= 1
            playerLocation[1] += 1
    elif direction == 'south-east':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] + 1, playerLocation[1] - 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            playerLocation[0] += 1
            playerLocation[1] -= 1
    elif direction == 'south-west':
        try:
            fieldIsThere = cursor.set_key(pack('III', playerLocation[0] - 1, playerLocation[1] - 1, playerLocation[2]))
        except error:
            fieldIsThere = False
        if fieldIsThere == True:
            playerLocation[0] -= 1
            playerLocation[1] -= 1
    if fieldIsThere == True:
        txn = env.begin(db=characterDB, write=True)
        cursor = txn.cursor(db=characterDB)
        accountID = clientHandler.loggedInAccount
        character = cursor.get(pack('I', accountID))
        character = literal_eval(character.decode())
        character['location'] = playerLocation
        cursor.put(pack('I', accountID), bytes(repr(character).encode()))
        txn.commit()
        updateArea = getPlayerArea(clientHandler, env, staticWorldDB, characterDB)
        return updateArea
    else:
        return 'destination invalid'

