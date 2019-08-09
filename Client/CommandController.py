import MainGameScreen
import GameState
from ServerConnect import *

# Module which handles the commands that the user inputs

# This performs any offline commands that the user inputs
def doOfflineCommandAction(commandAction):
    if commandAction == 'change screen config':
        GameState.screenUpdateQueue.put([['outputArea1Function', 'inventoryWindow'], ['outputArea2Function', 'commandOutputWindow'], ['outputArea3Function', 'playerInfoWindow'], ['outputArea4Function', 'chatWindow']])

# This checks if the inputted command is formatted correctly and exists
def checkGivenCommand(command):
    commandList = command.lower().split(' ')
    for word in commandList:
        if word == ' ':
            commandList.remove(word)
    if commandList == ['change', 'screen', 'config']:
        commandAction = 'change screen config'
        doOfflineCommandAction(commandAction)
    elif commandList == ['go', 'north']:
        sendCommandToServer('go north')

