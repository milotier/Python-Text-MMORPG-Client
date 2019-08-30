import lmdb
from struct import pack, error
from ast import literal_eval
from re import search
from passlib.hash import bcrypt

# Module which handles all database transactions

# TODO: Split database module up into multiple smaller ones?
# TODO: Make a difference between usernames and characternames
# TODO: Add some sort of character description
# TODO: Add an item system


# This starts up the lmdb environment and the databases in it
def startupDatabase():
    env = lmdb.open('GameDatabase', map_size=1000000, max_dbs=20)
    staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
    accountDB = env.open_db(bytes('Accounts'.encode()))
    return env, staticWorldDB, accountDB


def checkPasswordStrength(password):
    digits = search(r'\d', password)
    lowerCaseLetters = search(r'[a-z]', password)
    upperCaseLetters = search(r'[A-Z]', password)
    symbols = search(r"\W", password)

    if digits is not None and \
       lowerCaseLetters is not None and \
       upperCaseLetters is not None and \
       symbols is not None and len(password) >= 8:
        passwordIsStrongEnough = True
    else:
        passwordIsStrongEnough = False
    return passwordIsStrongEnough


def checkUsername(username, env, loginDB):
    if len(username) > 15:
        return 'username too long'
    elif len(username) < 1:
        return 'username too short'
    txn = env.begin(db=loginDB, write=True)
    cursor = txn.cursor(db=loginDB)
    username = cursor.get(bytes(username.encode()))
    if username is None:
        usernameExists = False
    else:
        usernameExists = True
    return usernameExists


def createAccount(username, password, env, loginDB, characterDB, accountDB):
    hashedPassword = bcrypt.hash(password)
    txn = env.begin(db=accountDB, write=True)
    cursor = txn.cursor(db=accountDB)
    currentID = 0
    accountID = None
    while accountID is None:
        accountExists = cursor.set_key(pack('I', currentID))
        if not accountExists:
            accountID = currentID
        else:
            currentID += 1

    account = bytes(repr({'username': username, 'status': 'Owner'}).encode())
    cursor.put(pack('I', accountID), account)
    cursor.close()
    txn.commit()
    txn = env.begin(db=loginDB, write=True)
    cursor = txn.cursor(db=loginDB)
    account = {'ID': accountID, 'password': hashedPassword}
    username = bytes(username.encode())
    account = bytes(repr(account).encode())
    cursor.put(username, account)
    cursor.close()
    txn.commit()
    txn = env.begin(db=characterDB, write=True)
    cursor = txn.cursor(db=characterDB)
    character = {'location': [1, 1, 5]}
    character = bytes(repr(character).encode())
    cursor.put(pack('I', accountID), character)
    cursor.close()
    txn.commit()
    return accountID


def checkAccountDetails(clientHandler, username, password, env, loginDB):
    txn = env.begin(db=loginDB)
    cursor = txn.cursor(db=loginDB)
    detailsMatch = False
    account = cursor.get(bytes(username.encode()))
    if account is not None:
        account = literal_eval(account.decode())
        passwordsMatch = bcrypt.verify(password, account['password'])
        if passwordsMatch is True:
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
            except error:
                isValidField = False
            if isValidField:
                fieldKey = repr(xCoord) + ' ' + repr(yCoord) + ' ' + repr(zCoord)

                if fieldIsThere:
                    field = literal_eval(cursor.value().decode())
                    updateArea[fieldKey] = field
            yCoord -= 1
        xCoord += 1
        yCoord = playerLocation[1] + 1
    return updateArea


def getCompleteUpdate(clientHandler, env, staticWorldDB, characterDB):
    update = {}
    area = getPlayerArea(clientHandler, env, staticWorldDB, characterDB)
    update['fields'] = {}
    update['fields']['update'] = area
    characterLocation = getPlayerLocation(clientHandler,
                                          env,
                                          characterDB)
    update['characterLocation'] = repr(characterLocation[0]) + \
                            ' ' + repr(characterLocation[1]) + \
                            ' ' + repr(characterLocation[2])
    return update


# This moves the player in the given direction
def movePlayer(clientHandler, direction, env, staticWorldDB, characterDB):
    playerLocation = getPlayerLocation(clientHandler, env, characterDB)
    txn = env.begin(db=staticWorldDB)
    cursor = txn.cursor(db=staticWorldDB)
    update = {'fields': {}}
    fieldIsThere = False
    xCoord = playerLocation[0]
    yCoord = playerLocation[1]
    zCoord = playerLocation[2]
    oldArea = getPlayerArea(clientHandler,
                            env,
                            staticWorldDB,
                            characterDB)
    if direction == 'north':
        try:
            newCoords = pack('III', xCoord, yCoord + 1, zCoord)
            fieldIsThere = cursor.set_key(newCoords)
        except error:
            fieldIsThere = False
        if fieldIsThere:
            yCoord += 1
    elif direction == 'south':
        try:
            newCoords = pack('III', xCoord, yCoord - 1, zCoord)
            fieldIsThere = cursor.set_key(newCoords)
        except error:
            fieldIsThere = False
        if fieldIsThere:
            yCoord -= 1
    elif direction == 'east':
        try:
            newCoords = pack('III', xCoord + 1, yCoord, zCoord)
            fieldIsThere = cursor.set_key(newCoords)
        except error:
            fieldIsThere = False
        if fieldIsThere:
            xCoord += 1
    elif direction == 'west':
        try:
            newCoords = pack('III', xCoord - 1, yCoord, zCoord)
            fieldIsThere = cursor.set_key(newCoords)
        except error:
            fieldIsThere = False
        if fieldIsThere:
            xCoord -= 1
    elif direction == 'north-east':
        try:
            newCoords = pack('III', xCoord + 1, yCoord + 1, zCoord)
            fieldIsThere = cursor.set_key(newCoords)
        except error:
            fieldIsThere = False
        if fieldIsThere:
            xCoord += 1
            yCoord += 1
    elif direction == 'north-west':
        try:
            newCoords = pack('III', xCoord - 1, yCoord + 1, zCoord)
            fieldIsThere = cursor.set_key(newCoords)
        except error:
            fieldIsThere = False
        if fieldIsThere:
            xCoord -= 1
            yCoord += 1
    elif direction == 'south-east':
        try:
            newCoords = pack('III', xCoord + 1, yCoord - 1, zCoord)
            fieldIsThere = cursor.set_key(newCoords)
        except error:
            fieldIsThere = False
        if fieldIsThere:
            xCoord += 1
            yCoord -= 1
    elif direction == 'south-west':
        try:
            newCoords = pack('III', xCoord - 1, yCoord - 1, zCoord)
            fieldIsThere = cursor.set_key(newCoords)
        except error:
            fieldIsThere = False
        if fieldIsThere:
            xCoord -= 1
            yCoord -= 1
    if fieldIsThere:
        txn = env.begin(db=characterDB, write=True)
        cursor = txn.cursor(db=characterDB)
        accountID = clientHandler.loggedInAccount
        character = cursor.get(pack('I', accountID))
        character = literal_eval(character.decode())
        character['location'] = [xCoord, yCoord, zCoord]
        update['characterLocation'] = repr(xCoord) + \
            ' ' \
            + \
            repr(yCoord) \
            + \
            ' ' \
            + \
            repr(zCoord)
        character = bytes(repr(character).encode())
        cursor.put(pack('I', accountID), character)
        txn.commit()
        newArea = getPlayerArea(clientHandler,
                                env,
                                staticWorldDB,
                                characterDB)
        for area in oldArea:
            if area in newArea:
                if 'update' in update['fields']:
                    update['fields']['update'][area] = newArea[area]
                else:
                    update['fields'].update({'update': {}})
                    update['fields']['update'][area] = newArea[area]
            else:
                if 'remove' in update['fields']:
                    update['fields']['remove'][area] = oldArea[area]
                else:
                    update['fields'].update({'remove': {}})
                    update['fields']['remove'][area] = oldArea[area]
        return update
    else:
        return 'destination invalid'
