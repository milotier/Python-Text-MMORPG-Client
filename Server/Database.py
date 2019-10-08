import lmdb
from struct import pack, error
from ast import literal_eval
from re import search
from passlib.hash import bcrypt
import json

# Module which handles all database transactions

# TODO: Split database module up into multiple smaller ones?
# TODO: Make a difference between usernames and characternames
# TODO: Add some sort of character description


# This starts up the lmdb environment and the databases in it
def startupDatabase():
    env = lmdb.open('GameDatabase', map_size=1000000, max_dbs=20)
    staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
    accountDB = env.open_db(bytes('Accounts'.encode()))
    return env, staticWorldDB, accountDB


# This checks if a password is strong enough
def checkPasswordStrength(password):
    digits = search(r'\d', password)
    lowerCaseLetters = search(r'[a-z]', password)
    upperCaseLetters = search(r'[A-Z]', password)
    symbols = search(r"\W", password)
    underScores = search(r"_", password)

    if digits is not None and \
       lowerCaseLetters is not None and \
       upperCaseLetters is not None and \
       symbols is not None or \
       underScores is not None and len(password) >= 8:
        passwordIsStrongEnough = True
    else:
        passwordIsStrongEnough = False
    return passwordIsStrongEnough


# This checks if a username can be used for an account
def checkUsername(username, txn, loginDB):
    if len(username) > 15:
        return 'username too long'
    elif len(username) < 1:
        return 'username too short'
    cursor = txn.cursor(db=loginDB)
    username = cursor.get(bytes(username.encode()))
    if username is None:
        usernameExists = False
    else:
        usernameExists = True
    return usernameExists


# This will create a new account
def createAccount(username,
                  password,
                  env,
                  loginDB,
                  characterDB,
                  characterLocationDB,
                  accountDB,
                  inventoryDB):
    passwordIsStrongEnough = checkPasswordStrength(password)
    txn = env.begin(write=True)
    usernameOutcome = checkUsername(username, txn, loginDB)
    if not passwordIsStrongEnough:
        return 'password too weak'
    elif usernameOutcome:
        return 'username already exists'
    elif type(usernameOutcome) == str:
        return usernameOutcome

    with open('config.json') as configData:
        config = json.load(configData)
    startingLocation = config['starting location']

    hashedPassword = bcrypt.hash(password)
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
    character = {'location': startingLocation}
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


# This puts the player in the characterLocationDB
def login(clientHandler,
          env,
          characterDB,
          characterLocationDB,
          updateDict,
          updateLock):
    accountID = clientHandler.loggedInAccount
    txn = env.begin(write=True)
    characterLocation = getPlayerLocation(clientHandler, txn, characterDB)
    characterLocationField = getPlayerLocationField(clientHandler,
                                                    txn,
                                                    characterDB,
                                                    characterLocationDB,
                                                    getValues=False)
    characterLocationString = repr(characterLocation[0]) + ' ' + \
                              repr(characterLocation[1]) + ' ' + \
                              repr(characterLocation[2])
    characterLocationField.append(accountID)
    cursor = txn.cursor(db=characterLocationDB)
    cursor.put(pack('III', characterLocation[0],
                           characterLocation[1],
                           characterLocation[2]),
               bytes(repr(characterLocationField).encode()))
    cursor.close()
    updatedCharacterLocationField = getPlayerLocationField(clientHandler,
                                                           txn,
                                                           characterDB,
                                                           characterLocationDB)
    characterLocationArea = getPlayerLocationArea(clientHandler,
                                                  txn,
                                                  characterDB,
                                                  characterLocationDB)
    txn.commit()
    updates = {}
    for field in characterLocationArea:
        for character in characterLocationArea[field]:
            character = character['ID']
            if character != accountID:
                updatedField = updatedCharacterLocationField.copy()
                for otherCharacter in updatedField:
                    if otherCharacter['ID'] == character:
                        updatedField.remove(otherCharacter)
                updates[character] = {}
                updates[character]['characterLocations'] = {}
                updates[character]['characterLocations']['update'] = {}
                updates[character]['characterLocations']['update'][characterLocationString] = updatedField
    with updateLock:
        for item in updates:
            updates[item]['type'] = 'update'
            if item not in updateDict:
                updateDict[item] = []
                updateDict[item].append(updates[item])
            else:
                updateDict[item].append(updates[item])


def logout(clientHandler,
           env,
           characterDB,
           characterLocationDB,
           updateDict,
           updateLock):
    accountID = clientHandler.loggedInAccount
    txn = env.begin(write=True)
    characterLocation = getPlayerLocation(clientHandler, txn, characterDB)
    characterLocationField = getPlayerLocationField(clientHandler,
                                                    txn,
                                                    characterDB,
                                                    characterLocationDB,
                                                    getValues=False)
    characterLocationString = repr(characterLocation[0]) + ' ' + \
                              repr(characterLocation[1]) + ' ' + \
                              repr(characterLocation[2])
    characterLocationField.remove(accountID)
    cursor = txn.cursor(db=characterLocationDB)
    cursor.put(pack('III', characterLocation[0],
                           characterLocation[1],
                           characterLocation[2]),
               bytes(repr(characterLocationField).encode()))
    cursor.close()
    characterLocationField = getPlayerLocationField(clientHandler,
                                                    txn,
                                                    characterDB,
                                                    characterLocationDB)
    characterLocationArea = getPlayerLocationArea(clientHandler,
                                                  txn,
                                                  characterDB,
                                                  characterLocationDB)
    txn.commit()
    updates = {}
    for field in characterLocationArea:
        for character in characterLocationArea[field]:
            character = character['ID']
            if character != accountID:
                updatedField = characterLocationField.copy()
                for otherCharacter in updatedField:
                    if otherCharacter['ID'] == character:
                        updatedField.remove(otherCharacter)
                updates[character] = {}
                updates[character]['characterLocations'] = {}
                updates[character]['characterLocations']['update'] = {}
                updates[character]['characterLocations']['update'][characterLocationString] = updatedField
    with updateLock:
        for item in updates:
            updates[item]['type'] = 'update'
            if item not in updateDict:
                updateDict[item] = []
                updateDict[item].append(updates[item])
            else:
                updateDict[item].append(updates[item])


# This gets the location of a character
def getPlayerLocation(clientHandler, txn, characterDB):
    cursor = txn.cursor(db=characterDB)
    accountID = clientHandler.loggedInAccount
    character = cursor.get(pack('I', accountID))
    character = literal_eval(character.decode())
    playerLocation = character['location']
    cursor.close()
    return playerLocation


# This gets all characters in the field a character is in
def getPlayerLocationField(clientHandler,
                           txn,
                           characterDB,
                           characterLocationDB,
                           getValues=True):
    playerLocation = getPlayerLocation(clientHandler, txn, characterDB)
    cursor = txn.cursor(db=characterLocationDB)
    playerLocationField = cursor.get(pack('III',
                                          playerLocation[0],
                                          playerLocation[1],
                                          playerLocation[2]))
    cursor.close()
    characterLocationField = literal_eval(playerLocationField.decode())
    if getValues:
        characterValueList = []
        cursor = txn.cursor(db=characterDB)
        for character in characterLocationField:
            cursor.set_key(pack('I', character))
            characterValue = cursor.value()
            characterValue = literal_eval(characterValue.decode())
            characterValue['ID'] = character
            characterValueList.append(characterValue)
        cursor.close()
        return characterValueList
    else:
        return characterLocationField


# This gets the characters in the fields on and around a character
def getPlayerLocationArea(clientHandler,
                          txn,
                          characterDB,
                          characterLocationDB):
    playerLocation = getPlayerLocation(clientHandler, txn, characterDB)
    playerLocationArea = {}
    xCoord = playerLocation[0] - 1
    yCoord = playerLocation[1] + 1
    zCoord = playerLocation[2]
    cursor = txn.cursor(db=characterLocationDB)
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
                    playerLocationArea[fieldKey] = field
            yCoord -= 1
        xCoord += 1
        yCoord = playerLocation[1] + 1
    cursor.close()
    cursor = txn.cursor(db=characterDB)
    characterValueArea = {}
    for field in playerLocationArea:
        characterList = playerLocationArea[field]
        characterValueList = []
        for character in characterList:
            cursor.set_key(pack('I', character))
            characterValue = cursor.value()
            characterValue = literal_eval(characterValue.decode())
            characterValue['ID'] = character
            characterValueList.append(characterValue)
        characterValueArea[field] = characterValueList
    return characterValueArea


# This gets the fields on and around a character
def getPlayerArea(clientHandler, txn, staticWorldDB, characterDB):
    playerLocation = getPlayerLocation(clientHandler, txn, characterDB)
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


# This gets all items in the field a character is in
def getPlayerItemField(clientHandler,
                       txn,
                       itemLocationDB,
                       itemDB,
                       characterDB):
    playerLocation = getPlayerLocation(clientHandler,
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
        itemValue['ID'] = item
        itemValueList.append(itemValue)
    return itemValueList


# This gets all the items in the fields on and around a character
def getPlayerItemArea(clientHandler,
                      txn,
                      itemLocationDB,
                      itemDB,
                      characterDB):
    playerLocation = getPlayerLocation(clientHandler,
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
        for item in itemList:
            cursor.set_key(pack('I', item))
            itemValue = cursor.value()
            itemValue = literal_eval(itemValue.decode())
            itemValue['ID'] = item
            itemValueList.append(itemValue)
        itemValueArea[field] = itemValueList
    cursor.close()
    return itemValueArea


# This gets the inventory of a character
def getPlayerInventory(clientHandler,
                       txn,
                       itemDB,
                       inventoryDB):
    cursor = txn.cursor(db=inventoryDB)
    accountID = clientHandler.loggedInAccount
    inventory = cursor.get(pack('I', accountID))
    cursor.close()
    inventory = literal_eval(inventory.decode())
    itemValueList = []
    cursor = txn.cursor(db=itemDB)
    for item in inventory:
        cursor.set_key(pack('I', item))
        itemValue = cursor.value()
        itemValue = literal_eval(itemValue.decode())
        itemValue['ID'] = item
        itemValueList.append(itemValue)
    return itemValueList


# This gets all the data a client needs and makes an update
def getCompleteUpdate(clientHandler,
                      env,
                      staticWorldDB,
                      characterDB,
                      characterLocationDB,
                      itemDB,
                      itemLocationDB,
                      inventoryDB):
    txn = env.begin(write=True)
    update = {}
    characterLocation = getPlayerLocation(clientHandler,
                                          txn,
                                          characterDB)
    update['characterLocation'] = repr(characterLocation[0]) + ' ' + \
                                  repr(characterLocation[1]) + ' ' + \
                                  repr(characterLocation[2])
    characterLocationArea = getPlayerLocationArea(clientHandler,
                                                  txn,
                                                  characterDB,
                                                  characterLocationDB)
    for field in characterLocationArea:
        for character in characterLocationArea[field]:
            if character['ID'] == clientHandler.loggedInAccount:
                characterLocationArea[field].remove(character)
    update['characterLocations'] = {}
    update['characterLocations']['update'] = characterLocationArea
    update['staticFields'] = {}
    update['itemLocations'] = {}
    area = getPlayerArea(clientHandler, txn, staticWorldDB, characterDB)
    update['staticFields']['update'] = area
    itemArea = getPlayerItemArea(clientHandler,
                                 txn,
                                 itemLocationDB,
                                 itemDB,
                                 characterDB)
    update['itemLocations']['update'] = itemArea
    inventory = getPlayerInventory(clientHandler,
                                   txn,
                                   itemDB,
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
               characterLocationDB,
               itemDB,
               itemLocationDB):

    # OG: the field the player was in before the command
    # old: before the changes to the field were made

    accountID = clientHandler.loggedInAccount
    txn = env.begin(write=True)
    playerLocation = getPlayerLocation(clientHandler, txn, characterDB)
    xCoord = playerLocation[0]
    yCoord = playerLocation[1]
    zCoord = playerLocation[2]

    # Here data is collected for comparison at the end to make the updates
    oldOGArea = getPlayerArea(clientHandler,
                              txn,
                              staticWorldDB,
                              characterDB)
    oldOGItemArea = getPlayerItemArea(clientHandler,
                                      txn,
                                      itemLocationDB,
                                      itemDB,
                                      characterDB)
    oldOGcharacterLocationArea = getPlayerLocationArea(clientHandler,
                                                       txn,
                                                       characterDB,
                                                       characterLocationDB)

    # This changes the coordinates of the character depending on the direction
    # after it has checked that the field actually exists
    cursor = txn.cursor(db=staticWorldDB)
    directions = {'north': (0, 1, 0),
                  'south': (0, -1, 0),
                  'east': (1, 0, 0),
                  'west': (-1, 0, 0),
                  'north-east': (1, 1, 0),
                  'north-west': (-1, 1, 0),
                  'south-east': (1, -1, 0),
                  'south-west': (-1, -1, 0)}
    coordChanges = directions[direction]
    try:
        newCoords = pack('III',
                         xCoord + coordChanges[0],
                         yCoord + coordChanges[1],
                         zCoord + coordChanges[2])
        fieldIsThere = cursor.set_key(newCoords)
    except error:
        fieldIsThere = False
    if fieldIsThere:
        xCoord += coordChanges[0]
        yCoord += coordChanges[1]
        zCoord += coordChanges[2]
    cursor.close()

    if not fieldIsThere:
        return 'destination invalid'

    # This removes the character from it's original characterLocationField
    oldOGCharacterLocationField = getPlayerLocationField(
        clientHandler,
        txn,
        characterDB,
        characterLocationDB,
        getValues=False)
    oldOGCharacterLocationField.remove(accountID)
    cursor = txn.cursor(db=characterLocationDB)
    oldPlayerLocation = \
        repr(playerLocation[0]) + ' ' + \
        repr(playerLocation[1]) + ' ' + \
        repr(playerLocation[2])
    cursor.put(pack('III',
                    playerLocation[0],
                    playerLocation[1],
                    playerLocation[2]),
               bytes(repr(oldOGCharacterLocationField).encode()))
    cursor.close()

    # This gets the updated version of the original characterLocationField
    OGCharacterLocationField = getPlayerLocationField(clientHandler,
                                                      txn,
                                                      characterDB,
                                                      characterLocationDB)

    update = {'staticFields': {}}

    # This updates the character's location in the database
    cursor = txn.cursor(db=characterDB)
    character = cursor.get(pack('I', accountID))
    character = literal_eval(character.decode())
    character['location'] = [xCoord, yCoord, zCoord]
    update['characterLocation'] = \
        repr(xCoord) + ' ' + \
        repr(yCoord) + ' ' + \
        repr(zCoord)
    character = bytes(repr(character).encode())
    cursor.put(pack('I', accountID), character)
    cursor.close()

    # This adds the player that typed the command to it's target location
    oldCharacterLocationField = getPlayerLocationField(clientHandler,
                                                       txn,
                                                       characterDB,
                                                       characterLocationDB,
                                                       getValues=False)
    oldCharacterLocationField.append(accountID)
    cursor = txn.cursor(db=characterLocationDB)
    cursor.put(pack('III',
                    xCoord,
                    yCoord,
                    zCoord),
               bytes(repr(oldCharacterLocationField).encode()))
    cursor.close()

    # This makes the update for the player that typed the command
    area = getPlayerArea(clientHandler,
                         txn,
                         staticWorldDB,
                         characterDB)
    for field in area:
        if field not in oldOGArea:
            if 'update' in update['staticFields']:
                update['staticFields']['update'][field] = area[field]
            else:
                update['staticFields'].update({'update': {}})
                update['staticFields']['update'][field] = area[field]

    for field in oldOGArea:
        if field not in area:
            if 'remove' in update['staticFields']:
                update['staticFields']['remove'][field] = oldOGArea[field]
            else:
                update['staticFields'].update({'remove': {}})
                update['staticFields']['remove'][field] = oldOGArea[field]
    update['itemLocations'] = {}
    itemArea = getPlayerItemArea(clientHandler,
                                 txn,
                                 itemLocationDB,
                                 itemDB,
                                 characterDB)
    for field in itemArea:
        if field not in oldOGArea:
            if 'update' in update['itemLocations']:
                update['itemLocations']['update'][field] = itemArea[field]
            else:
                update['itemLocations'].update({'update': {}})
                update['itemLocations']['update'][field] = itemArea[field]

    for field in oldOGArea:
        if field not in itemArea:
            if 'remove' in update['itemLocations']:
                update['itemLocations']['remove'][field] = oldOGItemArea[field]
            else:
                update['itemLocations'].update({'remove': {}})
                update['itemLocations']['remove'][field] = oldOGItemArea[field]
    update['characterLocations'] = {}
    characterLocationArea = getPlayerLocationArea(clientHandler,
                                                  txn,
                                                  characterDB,
                                                  characterLocationDB)
    for field in characterLocationArea:
        for character in characterLocationArea[field]:
            if character['ID'] == accountID:
                characterLocationArea[field].remove(character)
    for field in characterLocationArea:
        if field not in oldOGArea or oldOGArea[field] != characterLocationArea[field]:
            if 'update' in update['characterLocations']:
                update['characterLocations']['update'][field] = characterLocationArea[field]
            else:
                update['characterLocations'].update({'update': {}})
                update['characterLocations']['update'][field] = characterLocationArea[field]

    for field in oldOGArea:
        if field not in characterLocationArea:
            if 'remove' in update['characterLocations']:
                update['characterLocations']['remove'][field] = oldOGcharacterLocationArea[field]
            else:
                update['characterLocations'].update({'remove': {}})
                update['characterLocations']['remove'][field] = oldOGcharacterLocationArea[field]
    newCharacterLocationField = getPlayerLocationField(clientHandler,
                                                       txn,
                                                       characterDB,
                                                       characterLocationDB)
    txn.commit()

    # This makes the updates for other players close to
    # the player that typed the command
    updates = {}
    updates[accountID] = update
    for location in characterLocationArea:
        for character in characterLocationArea[location]:
            character = character['ID']
            if character != accountID:
                updatedNewCharacterLocationField = newCharacterLocationField.copy()
                for otherCharacter in updatedNewCharacterLocationField:
                    if otherCharacter['ID'] == character:
                        updatedNewCharacterLocationField.remove(otherCharacter)
                updatedOldCharacterLocationField = OGCharacterLocationField.copy()
                for otherCharacter in updatedOldCharacterLocationField:
                    if otherCharacter['ID'] == character:
                        updatedOldCharacterLocationField.remove(otherCharacter)
                updates[character] = {}
                updates[character]['characterLocations'] = {}
                updates[character]['characterLocations']['update'] = {}
                updates[character]['characterLocations']['update'][update['characterLocation']] = updatedNewCharacterLocationField
                updates[character]['characterLocations']['update'][oldPlayerLocation] = updatedOldCharacterLocationField
    return updates


def takeItem(clientHandler,
             targetItem,
             env,
             inventoryDB,
             itemLocationDB,
             itemDB,
             characterDB,
             characterLocationDB):
    accountID = clientHandler.loggedInAccount
    txn = env.begin(write=True)
    itemField = getPlayerItemField(clientHandler,
                                   txn,
                                   itemLocationDB,
                                   itemDB,
                                   characterDB)
    itemExists = False
    for fieldItem in itemField:
        if fieldItem['name'] == targetItem.itemName:
            itemExists = True
            pickedUpItem = fieldItem
            break
    if not itemExists:
        return 'item nonexisting'
    playerLocation = getPlayerLocation(clientHandler,
                                       txn,
                                       characterDB)
    cursor = txn.cursor(db=itemLocationDB)
    itemField.remove(pickedUpItem)
    newItemField = []
    for fieldItem in itemField:
        newItem = fieldItem['ID']
        newItemField.append(newItem)
    cursor.put(pack('III',
                    playerLocation[0],
                    playerLocation[1],
                    playerLocation[2]),
               bytes(repr(newItemField).encode()))
    cursor.close()
    inventory = getPlayerInventory(clientHandler,
                                   txn,
                                   itemDB,
                                   inventoryDB)
    inventory.append(pickedUpItem)
    dictInInventory = False
    for item in inventory:
        if isinstance(item, dict):
            dictInInventory = True
    while dictInInventory:
        for item in inventory:
            if type(item) != int:
                inventory.remove(item)
                inventory.append(item['ID'])
        dictInInventory = False
        for item in inventory:
            if isinstance(item, dict):
                dictInInventory = True
    cursor = txn.cursor(db=inventoryDB)
    cursor.put(pack('I', accountID), bytes(repr(inventory).encode()))
    cursor.close()
    playerLocation = \
        repr(playerLocation[0]) + ' ' + \
        repr(playerLocation[1]) + ' ' + \
        repr(playerLocation[2])
    update = {}
    update['itemLocations'] = {}
    update['itemLocations']['update'] = {}
    update['itemLocations']['update'][playerLocation] = itemField
    update['inventory'] = {}
    update['inventory']['update'] = [pickedUpItem]
    updates = {}
    updates[accountID] = update
    characterLocationArea = getPlayerLocationArea(clientHandler,
                                                  txn,
                                                  characterDB,
                                                  characterLocationDB)
    txn.commit()
    for location in characterLocationArea:
        for character in characterLocationArea[location]:
            character = character['ID']
            if character != accountID:
                updates[character] = {}
                updates[character]['itemLocations'] = {}
                updates[character]['itemLocations']['update'] = {}
                updates[character]['itemLocations']['update'][playerLocation] = itemField
    return updates


def dropItem(clientHandler,
             targetItem,
             env,
             inventoryDB,
             itemLocationDB,
             itemDB,
             characterDB,
             characterLocationDB):
    accountID = clientHandler.loggedInAccount
    txn = env.begin(write=True)
    inventory = getPlayerInventory(clientHandler,
                                   txn,
                                   itemDB,
                                   inventoryDB)
    itemExists = False
    for inventoryItem in inventory:
        if inventoryItem['name'] == targetItem.itemName:
            itemExists = True
            droppedItem = inventoryItem
            break
    if not itemExists:
        return 'item nonexisting'
    playerLocation = getPlayerLocation(clientHandler,
                                       txn,
                                       characterDB)
    cursor = txn.cursor(db=inventoryDB)
    inventory.remove(droppedItem)
    dictInInventory = False
    for item in inventory:
        if isinstance(item, dict):
            dictInInventory = True
    while dictInInventory:
        for item in inventory:
            if type(item) != int:
                inventory.remove(item)
                inventory.append(item['ID'])
        dictInInventory = False
        for item in inventory:
            if isinstance(item, dict):
                dictInInventory = True
    cursor.put(pack('I', accountID), bytes(repr(inventory).encode()))
    cursor.close()
    itemField = getPlayerItemField(clientHandler,
                                   txn,
                                   itemLocationDB,
                                   itemDB,
                                   characterDB)
    itemField.append(droppedItem)
    cursor = txn.cursor(db=itemLocationDB)
    newItemField = []
    for fieldItem in itemField:
        newItem = fieldItem['ID']
        newItemField.append(newItem)
    cursor.put(pack('III',
                    playerLocation[0],
                    playerLocation[1],
                    playerLocation[2]),
               bytes(repr(newItemField).encode()))
    cursor.close()

    playerLocation = \
        repr(playerLocation[0]) + ' ' + \
        repr(playerLocation[1]) + ' ' + \
        repr(playerLocation[2])
    update = {}
    update['itemLocations'] = {}
    update['itemLocations']['update'] = {}
    update['itemLocations']['update'][playerLocation] = itemField
    update['inventory'] = {}
    update['inventory']['remove'] = [droppedItem]
    updates = {}
    updates[accountID] = update
    characterLocationArea = getPlayerLocationArea(clientHandler,
                                                  txn,
                                                  characterDB,
                                                  characterLocationDB)
    txn.commit()
    for location in characterLocationArea:
        for character in characterLocationArea[location]:
            character = character['ID']
            if character != accountID:
                updates[character] = {}
                updates[character]['itemLocations'] = {}
                updates[character]['itemLocations']['update'] = {}
                updates[character]['itemLocations']['update'][playerLocation] = itemField
    return updates
