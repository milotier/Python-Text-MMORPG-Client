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
    txn = env.begin(db=loginDB)
    cursor = txn.cursor(db=loginDB)
    username = cursor.get(bytes(username.encode()))
    if username is None:
        usernameExists = False
    else:
        usernameExists = True
    return usernameExists


def createAccount(username, password, env, loginDB, characterDB, accountDB, inventoryDB):
    hashedPassword = bcrypt.hash(password)
    txn = env.begin(write=True)
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

    cursor = txn.cursor(db=loginDB)
    account = {'ID': accountID, 'password': hashedPassword}
    username = bytes(username.encode())
    account = bytes(repr(account).encode())
    cursor.put(username, account)
    cursor.close()

    cursor = txn.cursor(db=characterDB)
    character = {'location': [1, 1, 5]}
    character = bytes(repr(character).encode())
    cursor.put(pack('I', accountID), character)
    cursor.close()

    cursor = txn.cursor(db=inventoryDB)
    cursor.put(pack('I', accountID), bytes(repr([]).encode()))
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


def getPlayerLocation(clientHandler, env, txn, characterDB):
    cursor = txn.cursor(db=characterDB)
    accountID = clientHandler.loggedInAccount
    character = cursor.get(pack('I', accountID))
    character = literal_eval(character.decode())
    playerLocation = character['location']
    cursor.close()
    return playerLocation


# This gets the nine (or less) fields on and around the player
def getPlayerArea(clientHandler, env, txn, staticWorldDB, characterDB):
    playerLocation = getPlayerLocation(clientHandler, env, txn, characterDB)
    updateArea = {}
    xCoord = playerLocation[0] - 1
    yCoord = playerLocation[1] + 1
    zCoord = playerLocation[2]
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


def getPlayerItemField(clientHandler,
                       env,
                       txn,
                       itemLocationDB,
                       itemDB,
                       characterDB):
    playerLocation = getPlayerLocation(clientHandler,
                                       env,
                                       txn,
                                       characterDB)
    cursor = txn.cursor(db=itemLocationDB)
    key = pack('III', playerLocation[0], playerLocation[1], playerLocation[2])
    itemField = cursor.get(key)
    itemField = literal_eval(itemField.decode())
    cursor.close()
    cursor = txn.cursor(db=itemDB)
    itemValueList = []
    for item in itemField:
        cursor.set_key(pack('I', item))
        itemValue = cursor.value()
        itemValue = literal_eval(itemValue.decode())
        itemValueList.append(itemValue)
    return itemValueList


# This gets all the items in the nine (or less) fields on and around the player
def getPlayerItemArea(clientHandler,
                      env,
                      txn,
                      itemLocationDB,
                      itemDB,
                      characterDB):
    playerLocation = getPlayerLocation(clientHandler,
                                       env,
                                       txn,
                                       characterDB)
    itemArea = {}
    xCoord = playerLocation[0] - 1
    yCoord = playerLocation[1] + 1
    zCoord = playerLocation[2]
    cursor = txn.cursor(db=itemLocationDB)
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
                    itemArea[fieldKey] = field
            yCoord -= 1
        xCoord += 1
        yCoord = playerLocation[1] + 1
    cursor.close()

    cursor = txn.cursor(db=itemDB)
    itemValueArea = {}
    for field in itemArea:
        itemList = itemArea[field]
        itemValueList = []
        print(itemList)
        for item in itemList:
            print(item)
            cursor.set_key(pack('I', item))
            itemValue = cursor.value()
            print(itemValue)
            itemValue = literal_eval(itemValue.decode())
            itemValueList.append(itemValue)
        itemValueArea[field] = itemValueList
    cursor.close()
    return itemValueArea


def getPlayerInventory(clientHandler, env, txn, inventoryDB):
    cursor = txn.cursor(db=inventoryDB)
    accountID = clientHandler.loggedInAccount
    inventory = cursor.get(pack('I', accountID))
    inventory = literal_eval(inventory.decode())
    return inventory


# This gets all the data a client needs
def getCompleteUpdate(clientHandler,
                      env,
                      staticWorldDB,
                      characterDB,
                      itemDB,
                      itemLocationDB,
                      inventoryDB):
    txn = env.begin(write=True)
    update = {}
    characterLocation = getPlayerLocation(clientHandler,
                                          env,
                                          txn,
                                          characterDB)
    update['characterLocation'] = repr(characterLocation[0]) + \
                            ' ' + repr(characterLocation[1]) + \
                            ' ' + repr(characterLocation[2])
    update['staticFields'] = {}
    update['itemLocations'] = {}
    area = getPlayerArea(clientHandler, env, txn, staticWorldDB, characterDB)
    update['staticFields']['update'] = area
    itemArea = getPlayerItemArea(clientHandler,
                                 env,
                                 txn,
                                 itemLocationDB,
                                 itemDB,
                                 characterDB)
    update['itemLocations']['update'] = itemArea
    inventory = getPlayerInventory(clientHandler,
                                   env,
                                   txn,
                                   inventoryDB)
    update['inventory'] = {}
    update['inventory']['update'] = inventory
    return update


# This moves the player in the given direction
def movePlayer(clientHandler,
               direction,
               env,
               staticWorldDB,
               characterDB,
               itemDB,
               itemLocationDB):
    txn = env.begin(write=True)
    playerLocation = getPlayerLocation(clientHandler, env, txn, characterDB)
    cursor = txn.cursor(db=staticWorldDB)
    update = {'staticFields': {}}
    fieldIsThere = False
    xCoord = playerLocation[0]
    yCoord = playerLocation[1]
    zCoord = playerLocation[2]
    oldArea = getPlayerArea(clientHandler,
                            env,
                            txn,
                            staticWorldDB,
                            characterDB)
    oldItemArea = getPlayerItemArea(clientHandler,
                                    env,
                                    txn,
                                    itemLocationDB,
                                    itemDB,
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
    cursor.close()
    if fieldIsThere:
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
        newArea = getPlayerArea(clientHandler,
                                env,
                                txn,
                                staticWorldDB,
                                characterDB)
        for area in newArea:
            if area not in oldArea:
                if 'update' in update['staticFields']:
                    update['staticFields']['update'][area] = newArea[area]
                else:
                    update['staticFields'].update({'update': {}})
                    update['staticFields']['update'][area] = newArea[area]

        for area in oldArea:
            if area not in newArea:
                if 'remove' in update['staticFields']:
                    update['staticFields']['remove'][area] = oldArea[area]
                else:
                    update['staticFields'].update({'remove': {}})
                    update['staticFields']['remove'][area] = oldArea[area]
        update['itemLocations'] = {}
        itemArea = getPlayerItemArea(clientHandler,
                                     env,
                                     txn,
                                     itemLocationDB,
                                     itemDB,
                                     characterDB)
        print(oldItemArea)
        for area in itemArea:
            if area not in oldArea:
                if 'update' in update['itemLocations']:
                    update['itemLocations']['update'][area] = itemArea[area]
                else:
                    update['itemLocations'].update({'update': {}})
                    update['itemLocations']['update'][area] = itemArea[area]

        for area in oldArea:
            if area not in itemArea:
                if 'remove' in update['itemLocations']:
                    update['itemLocations']['remove'][area] = oldItemArea[area]
                else:
                    update['itemLocations'].update({'remove': {}})
                    update['itemLocations']['remove'][area] = oldItemArea[area]
        txn.commit()
        print(update)
        return update
    else:
        return 'destination invalid'


def takeItem(clientHandler,
             targetItem,
             env,
             inventoryDB,
             itemLocationDB,
             itemDB,
             characterDB):
    txn = env.begin(write=True)
    itemField = getPlayerItemField(clientHandler,
                                   env,
                                   txn,
                                   itemLocationDB,
                                   itemDB,
                                   characterDB)
    itemExists = False
    for item in itemField:
        if item['name'] == targetItem.itemName:
            itemExists = True
            item = item
            break
    if itemExists:
        playerLocation = getPlayerLocation(clientHandler,
                                           env,
                                           txn,
                                           characterDB)
        cursor = txn.cursor(db=itemLocationDB)
        print(item)
        itemField.remove(item)
        newItemField = []
        for fieldItem in itemField:
            newItem = fieldItem['ID']
            newItemField.append(newItem)
        cursor.put(pack('III', playerLocation[0], playerLocation[1], playerLocation[2]), bytes(repr(newItemField).encode()))
        cursor.close()
        inventory = getPlayerInventory(clientHandler,
                                       env,
                                       txn,
                                       inventoryDB)
        accountID = clientHandler.loggedInAccount
        inventory.append(item)
        cursor = txn.cursor(db=inventoryDB)
        cursor.put(pack('I', accountID), bytes(repr(inventory).encode()))
        cursor.close()

        playerLocation = repr(playerLocation[0]) + ' ' + \
                         repr(playerLocation[1]) + ' ' + \
                         repr(playerLocation[2])
        update = {}
        update['itemLocations'] = {}
        update['itemLocations']['update'] = {}
        update['itemLocations']['update'][playerLocation] = itemField
        update['inventory'] = {}
        update['inventory']['update'] = [item]
        txn.commit()
        return update
    else:
        return 'item nonexisting'
        txn.commit()
