import MainGameScreen

def doOfflineCommandAction(commandAction):
    if commandAction == 'change screen config':
        MainGameScreen.screenUpdateQueue.put([['outputArea1Function', 'inventoryWindow'], ['outputArea2Function', 'commandOutputWindow'], ['outputArea3Function', 'playerInfoWindow'], ['outputArea4Function', 'chatWindow'], ['playerInfoWindowText', 'Testest'], ['commandOutputWindowText', 'Tester'], ['inventoryWindowText', 'Test'], ['chatWindowText', 'Testester']])

def checkGivenCommand(command):
    commandList = command.lower().split(' ')
    for word in commandList:
        if word == ' ':
            commandList.remove(word)
    if commandList == ['change', 'screen', 'config']:
        commandAction = 'change screen config'
        doOfflineCommandAction(commandAction)

