import MainGameScreen
import ServerConnect
from time import *
from threading import *
from sys import exit

host = '127.0.0.1'
port = 5555

def doScreenUpdates():
    while True:
        if MainGameScreen.screenUpdateQueue.empty() == False:
            screenUpdate = MainGameScreen.screenUpdateQueue.get()
            
            MainGameScreen.updateScreen(screenUpdate)
        sleep(0.05)

def startGame():
    print('You have been succesfully connected to the server.')
    getUpdatesFromServerThread = Thread(target=ServerConnect.getUpdatesFromServer, args=(MainGameScreen.screenUpdateQueue,))
    getUpdatesFromServerThread.daemon = True
    getUpdatesFromServerThread.start()
    screenUpdateThread = Thread(target=doScreenUpdates)
    screenUpdateThread.daemon = True
    screenUpdateThread.start()
    sleep(1)
    MainGameScreen.main()
    sleep(1)
    ServerConnect.sendCommandToServer('disconnect')

connectionOutcome = ServerConnect.connectToServer(host, port)
if connectionOutcome == 'succesfull connection':
    startGame()
else:
    print('\n\nFailed to connect to the server. Please check your internet connection. If your internet connection is okay, it probably means the server is down and you should wait for a while.\n\n')
