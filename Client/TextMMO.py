import ServerConnect
from time import sleep
from threading import Thread
from sys import exit
import GameState
from getpass import getpass
import MainGameScreen

# The main module which starts all the different threads
# and the application's eventloop

# The ip and port of the server
host = '127.0.0.1'
port = 5555

isLoggedIn = False


# This will be ran by the thread that handles the screen updates
def doScreenUpdates():
    sleep(0.5)
    while True:
        if not GameState.screenUpdateQueue.empty():
            screenUpdate = GameState.screenUpdateQueue.get()
            MainGameScreen.updateQueue.put(screenUpdate)
            GameState.updateState(screenUpdate, MainGameScreen.root)
        sleep(0.05)


# This starts up the threads and eventloop of the application
def startGame():
    print('\n\nYou have been succesfully connected to the server.\n\n')
    getUpdatesFromServerThread = Thread(
        target=ServerConnect.getUpdatesFromServer,
        args=(GameState.screenUpdateQueue,))
    getUpdatesFromServerThread.daemon = True
    getUpdatesFromServerThread.start()
    screenUpdateThread = Thread(target=doScreenUpdates)
    screenUpdateThread.daemon = True
    screenUpdateThread.start()
    MainGameScreen.runMainloop()
    # When the eventloop stops, this is ran
    # and sends a disconnect signal to the server, which closes the connection
    sleep(0.5)
    ServerConnect.sendCommandToServer('disconnect')


# This is ran at the start of the application
# which tries to connect to the server
# TODO: Replace input prompts with login screen
def login(iteration):
    if iteration == 'first':
        connectionOutcome = ServerConnect.connectToServer(host, port)
    else:
        connectionOutcome = 'successfull connection'
    tryAgain = False
    if connectionOutcome == 'successfull connection':
        validAnswer = False
        while not validAnswer:
            hasAccount = input('Do you have an account (y/n)? ')
            hasAccount = hasAccount.lower()
            if hasAccount == 'yes' or hasAccount == 'y':
                print('\nLogin to your account:\n\n')
                username = input('Please enter your username: ')
                password = getpass('Please enter your password: ')
                loginOutcome = ServerConnect.loginToAccount([username,
                                                             password])
                if type(loginOutcome) == dict:
                    GameState.screenUpdateQueue.put(loginOutcome)
                elif loginOutcome == 'no match found':
                    print('The username or password is incorrect.')
                    tryAgain = True
                validAnswer = True
            elif hasAccount == 'no' or hasAccount == 'n':
                print('\nMake a new account:\n\n')
                username = input('Please enter your username (warning: this is also your character name, and you won\'t be able to change it... yet): ')
                password = getpass('Please enter a password for your account. Make sure that it\'s a strong one! ')
                creationOutcome = ServerConnect.createAccount([username,
                                                               password])
                if creationOutcome == 'password too weak':
                    print('That password is not strong enough. It must at least contain one lowercase and uppercase letter, digit and symbol and 8 characters in total.')
                    tryAgain = True
                elif creationOutcome == 'username already exists':
                    print('That username has already been taken.')
                    tryAgain = True
                elif creationOutcome == 'username too long':
                    print('The maximum username length is 15.')
                    tryAgain = True
                elif creationOutcome == 'username too short':
                    print('The minimum username length is 1')
                    tryAgain = True
                else:
                    GameState.screenUpdateQueue.put(creationOutcome)
                validAnswer = True
    else:
        print('\n\nFailed to connect to the server.', end=' ')
        print('Please check your internet connection.', end=' ')
        print('If your internet connection is okay,', end=' ')
        print('it probably means the server is down', end=' ')
        print('and you should wait for a while.\n\n')
        exit()

    return tryAgain


try:
    tryAgain = login('first')
except KeyboardInterrupt:
    print('')
    exit()
while tryAgain:
    try:
        tryAgain = login(None)
    except KeyboardInterrupt:
        print('')
        exit()

startGame()
