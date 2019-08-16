import MainGameScreen
import GameState
from ServerConnect import *
import sys
import re
import time

# Module which handles the commands that the user inputs

class Direction:
    def __init__(self, direction, inputDirection, directionCommentFactor):
        self.direction = direction
        self.inputDirection = inputDirection
        self.directionCommentFactor = directionCommentFactor

class Command:
    def __init__(self, verbCommentFactor, inputVerb, commentFactorList):
        self.inputVerb = inputVerb
        self.verbCommentFactor = verbCommentFactor
        self.commentFactor = self.verbCommentFactor
        commentFactorNum = 0
        commentFactorNum = 1
        for commentFactor in commentFactorList:
            self.commentFactor += commentFactor
            commentFactorNum += 1
        self.commentFactor = commentFactor / commentFactorNum


class TravelCommand(Command):
    def __init__(self, inputVerb, verbCommentFactor, direction, inputDirection, directionCommentFactor):
        super().__init__(verbCommentFactor, inputVerb, [directionCommentFactor])
        self.direction = Direction(direction, inputDirection, directionCommentFactor)
    

# This performs any offline commands that the user inputs
def doOfflineCommandAction(commandAction):
    if commandAction == 'change screen config':
        GameState.screenUpdateQueue.put([['outputArea1Function', 'inventoryWindow'], ['outputArea2Function', 'commandOutputWindow'], ['outputArea3Function', 'skillWindow'], ['outputArea4Function', 'chatWindow']])


def lexGivenCommand(characters):
    tokenExprs = [
    (r'go',          True,          {'type': 'verb', 'verbType': 'travel', 'commentFactor': 1, 'input': 'go'}),
    (r'travel',      True,          {'type': 'verb', 'verbType': 'travel', 'commentFactor': 1, 'input': 'travel'}),
    (r'locomote',    True,          {'type': 'verb', 'verbType': 'travel', 'commentFactor': 2, 'input': 'locomote'}),
    (r'journey',     True,          {'type': 'verb', 'verbType': 'travel', 'commentFactor': 2, 'input': 'journey'}),
    (r'move',        True,          {'type': 'verb', 'verbType': 'travel', 'commentFactor': 1, 'input': 'move'}),
    (r'slither',     True,          {'type': 'verb', 'verbType': 'travel', 'commentFactor': 2, 'input': 'slither'}),
    (r'take',        True,          {'type': 'verb', 'verbType': 'take', 'commentFactor': 1, 'input': 'take'}),
    (r'confiscate',  True,          {'type': 'verb', 'verbType': 'take', 'commentFactor': 2, 'input': 'confiscate'}),
    (r'seize',       True,          {'type': 'verb', 'verbType': 'take', 'commentFactor': 1, 'input': 'seize'}),
    (r'pick',        True,          {'type': 'verb', 'verbType': 'pick', 'commentFactor': 1, 'input': 'pick'}),

    (r'up',          True,          {'type': 'keyword', 'keyword': 'up', 'commentFactor': 1, 'input': 'up'}),

    (r'north',       True,          {'type': 'direction', 'direction': 'north', 'commentFactor': 1, 'input': 'north'}),
    (r'n',           True,          {'type': 'direction', 'direction': 'north', 'commentFactor': 0, 'input': 'n'}),
    (r'south',       True,          {'type': 'direction', 'direction': 'south', 'commentFactor': 1, 'input': 'south'}),
    (r's',           True,          {'type': 'direction', 'direction': 'south', 'commentFactor': 0, 'input': 's'}),
    (r'east',        True,          {'type': 'direction', 'direction': 'east', 'commentFactor': 1, 'input': 'east'}),
    (r'e',           True,          {'type': 'direction', 'direction': 'east', 'commentFactor': 0, 'input': 'e'}),
    (r'west',        True,          {'type': 'direction', 'direction': 'west', 'commentFactor': 1, 'input': 'west'}),
    (r'w',           True,          {'type': 'direction', 'direction': 'west', 'commentFactor': 0, 'input': 'w'}),

    (r'[A-Za-z][A-Za-z0-9_]*', False, {'type': 'name'})
    ]
    tokens = []
    words = characters.split(' ')
    while '' in words:
        for word in words:
            if word == '':
                words.remove(word)

    for word in words:
        for tokenExpr in tokenExprs:
            if tokenExpr[1] == True: 
                if tokenExpr[0] == word:
                    token = tokenExpr[2]
                    tokens.append(token)
                    break
            
            else:
                regex = re.compile(tokenExpr[0])
                match = regex.match(word)
                if match: 
                    text = match.group(0)
                    token = tokenExpr[2]
                    token['input'] = text
                    immutableToken = frozenset(token.items())
                    tokens.append(immutableToken)  
                    break
    tokenList = []
    for token in tokens:
        if type(token) == frozenset:
            token = dict(token)
        tokenList.append(token)
    return tokenList

def parseGivenCommand(tokenList):
    command = None
    if tokenList[0]['type'] == 'verb':
        verb = tokenList[0]

        if verb['verbType'] == 'travel':
            if tokenList[1]['type'] == 'direction' and len(tokenList) == 2: 
                direction = tokenList[1]
                command = TravelCommand(verb['input'], verb['commentFactor'], direction['direction'], direction['input'], direction['commentFactor'])

    elif tokenList[0]['type'] == 'direction' and len(tokenList) == 1:
        token = tokenList[0]
        command = TravelCommand(None, 0, token['direction'], token['input'], token['commentFactor'])
    
    return command


# This checks if the inputted command is formatted correctly and exists
def checkGivenCommand(command):
    lexedCommand = lexGivenCommand(command)
    command = parseGivenCommand(lexedCommand)
    sendCommandToServer(command)

