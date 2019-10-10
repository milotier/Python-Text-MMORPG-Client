import ServerConnect
from time import sleep
from threading import Thread
from sys import exit
import GameState
from getpass import getpass
import MainGameScreen
import json

# The main module which starts all the different threads
# and the application's eventloop

# Here the IP and port of the server will be read from the config file
with open('config.json') as configData:
    config = json.load(configData)
if 'IP' in config:
    host = config['IP']
else:
    print('\n\n')
    print('IP address of server could not be found in the config file.', end=' ')
    print('Please make sure you specify an IP adress to connect to.')
    print('\n\n')
    exit()
if 'port' in config:
    port = config['port']
else:
    print('\n\n')
    print('Port of server could not be found in the config file.', end=' ')
    print('Please make sure you specify a port to use.')
    print('\n\n')
    exit()

# This is the client's version. If you change this, errors might appear
version = '0.1.0'


# This will be ran by the thread that handles the screen updates
def doScreenUpdates():
    while True:
        sleep(0.05)
        try:
            if not GameState.screenUpdateQueue.empty():
                screenUpdate = GameState.screenUpdateQueue.get()
                GameState.updateState(screenUpdate, MainGameScreen.root)
                MainGameScreen.updateQueue.put(screenUpdate)
        except AttributeError:
            GameState.screenUpdateQueue.put(screenUpdate)


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
        connectionOutcome = ServerConnect.connectToServer(host, port, version)
        if connectionOutcome == 'successfull connection':
            print('\nYou have been succesfully connected to the server.\n')
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
    elif connectionOutcome == 'version invalid':
        print('\n\n')
        print('A new version of this game is available on Github.', end=' ')
        print('Please download the new version at https://github.com/milotier/Python-Text-MMORPG to continue playing.')
        print('\n\n')
        exit()
    else:
        print('\n\n')
        print('Failed to connect to the server. This can mean a few things:')
        print('    -You don\'t have a good internet connection')
        print('    -The server you\'re trying to connect to is currently down')
        print('    -The IP or port specified in the config file are invalid')
        print('\n\n')
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
