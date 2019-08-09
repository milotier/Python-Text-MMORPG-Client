import MainGameScreen
import ServerConnect
from time import *
from threading import *
from sys import exit
import GameState

# The main module which starts all the different threads and the application's eventloop

# The ip and port of the server
host = '127.0.0.1'
port = 5555

# This will be ran by the thread that handles the screen updates
def doScreenUpdates():
    while True:
        if GameState.screenUpdateQueue.empty() == False:
            screenUpdate = GameState.screenUpdateQueue.get()
            GameState.updateState(screenUpdate, MainGameScreen.app)
            MainGameScreen.updateScreen()
        sleep(0.05)

# This starts up the threads and eventloop of the application
def startGame():
    print('You have been succesfully connected to the server.')
    MainGameScreen.updateScreen()
    getUpdatesFromServerThread = Thread(target=ServerConnect.getUpdatesFromServer, args=(GameState.screenUpdateQueue,))
    getUpdatesFromServerThread.daemon = True
    getUpdatesFromServerThread.start()
    screenUpdateThread = Thread(target=doScreenUpdates)
    screenUpdateThread.daemon = True
    screenUpdateThread.start()
    sleep(1)
    MainGameScreen.main()
    # When the eventloop stops, this is ran and sends a disconnect signal to the server, which closes the connection
    sleep(0.5)
    ServerConnect.sendCommandToServer('disconnect')
    print('\n\nYou have been disconnected from the server.\n\n')

# This is ran at the start of the application which tries to connect to the server
connectionOutcome = ServerConnect.connectToServer(host, port)
if connectionOutcome == 'successfull connection':
    startGame()
else:
    print('\n\nFailed to connect to the server. Please check your internet connection. If your internet connection is okay, it probably means the server is down and you should wait for a while.\n\n')
