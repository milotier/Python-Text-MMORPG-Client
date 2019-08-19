import MainGameScreen
import ServerConnect
from time import *
from threading import *
from sys import exit
import GameState
from getpass import *

# The main module which starts all the different threads and the application's eventloop

# The ip and port of the server
host = '127.0.0.1'
port = 5555

isLoggedIn = False

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
    print('\n\nYou have been succesfully connected to the server.\n\n')
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
def login(iteration):
    if iteration == 'first':
        connectionOutcome = ServerConnect.connectToServer(host, port)
    else:
        connectionOutcome = 'successfull connection'
    tryAgain = False
    if connectionOutcome == 'successfull connection':
        validAnswer = False
        while validAnswer == False:
            hasAccount = input('Do you have an account (y/n)? ')
            hasAccount = hasAccount.lower()
            if hasAccount == 'yes' or hasAccount == 'y':
                print('\nLogin to your account:\n\n')
                username = input('Please enter your username: ')
                password = getpass('Please enter your password: ')
                ServerConnect.loginToAccount([username, password])
                validAnswer = True
            elif hasAccount == 'no' or hasAccount == 'n':
                print('\nMake a new account:\n\n')
                username = input('Please enter your username (warning: this is also your character name, and you won\'t be able to change it... yet): ')
                password = getpass('Please enter a password for your account. Make sure that it\'s a strong one! ')
                creationOutcome = ServerConnect.createAccount([username, password])
                if creationOutcome == 'password too weak':
                    print('That password is not strong enough.')
                    tryAgain = True
                elif creationOutcome == 'username already exists':
                    print('That username has already been taken.')
                    tryAgain = True
                else:
                    GameState.screenUpdateQueue.put(creationOutcome)
                validAnswer = True
    else:
        print('\n\nFailed to connect to the server. Please check your internet connection. If your internet connection is okay, it probably means the server is down and you should wait for a while.\n\n')
        exit()

    return tryAgain

tryAgain = login('first')
while tryAgain == True:
    tryAgain = login(None)

startGame()