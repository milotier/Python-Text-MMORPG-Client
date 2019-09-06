from ServerConnect import sendCommandToServer
import re
from ast import literal_eval

# Module which handles the commands that the user inputs


# These are the different classes which make up the different commands
# TODO: Add more commands
class Direction:
    def __init__(self,
                 direction,
                 inputDirection,
                 directionCommentFactor):
        self.direction = direction
        self.inputDirection = inputDirection
        self.directionCommentFactor = directionCommentFactor


class Item:
    def __init__(self,
                 itemName):
        self.itemName = itemName


class Command:
    def __init__(self,
                 verbCommentFactor,
                 inputVerb,
                 commentFactorList):
        self.inputVerb = inputVerb
        self.verbCommentFactor = verbCommentFactor
        self.commentFactor = self.verbCommentFactor
        commentFactorNum = 0
        commentFactorNum = 1
        for commentFactor in commentFactorList:
            self.commentFactor += commentFactor
            commentFactorNum += 1
        self.commentFactor = self.commentFactor / commentFactorNum


class TravelCommand(Command):
    def __init__(self,
                 inputVerb,
                 verbCommentFactor,
                 direction,
                 inputDirection,
                 directionCommentFactor):
        super().__init__(verbCommentFactor,
                         inputVerb,
                         [directionCommentFactor])
        self.direction = Direction(direction,
                                   inputDirection,
                                   directionCommentFactor)


class TakeCommand(Command):
    def __init__(self,
                 inputVerb,
                 verbCommentFactor,
                 itemName):
        super().__init__(verbCommentFactor,
                         inputVerb,
                         [])
        self.targetItem = Item(itemName)


# This changes the string inputted by the player into a list of tokens
def lexGivenCommand(characters):
    tokenExprFile = open('regex.txt', 'r')
    tokenExprs = tokenExprFile.read()
    tokenExprs = literal_eval(tokenExprs)
    tokens = []
    words = characters.split(' ')
    while '' in words:
        for word in words:
            if word == '':
                words.remove(word)

    for word in words:
        for tokenExpr in tokenExprs:
            if tokenExpr[1]:
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


# This parses the list of tokens made by the lexer into a command object
def parseGivenCommand(tokenList):
    command = None
    if tokenList[0]['type'] == 'verb':
        verb = tokenList[0]

        if verb['verbType'] == 'travel':
            if tokenList[1]['type'] == 'direction' and len(tokenList) == 2:
                direction = tokenList[1]
                command = TravelCommand(verb['input'],
                                        verb['commentFactor'],
                                        direction['direction'],
                                        direction['input'],
                                        direction['commentFactor'])

        elif verb['verbType'] == 'take':
            index = 1
            itemName = ''
            while not index > len(tokenList) - 1:
                token = tokenList[index]
                if index == len(tokenList) - 1:
                    itemName += ' ' + token['input']
                    command = TakeCommand(verb['input'],
                                          verb['commentFactor'],
                                          itemName)
                if index == 1:
                    itemName += token['input']
                if index > 1:
                    itemName += ' ' + token['input']
                index += 1
        
        elif verb['verbType'] == 'pick' and tokenList[1]['type'] == 'keyword':
            if tokenList[1]['keyword'] == 'up':
                index = 2
                itemName = ''
                while not index > len(tokenList) - 1:
                    token = tokenList[index]
                    if index == len(tokenList) - 1:
                        itemName += ' ' + token['input']
                        command = TakeCommand(verb['input'],
                                            verb['commentFactor'],
                                            itemName)
                    if index == 2:
                        itemName += token['input']
                    if index > 2:
                        itemName += ' ' + token['input']
                    index += 1

    elif tokenList[0]['type'] == 'direction' and len(tokenList) == 1:
        token = tokenList[0]
        command = TravelCommand(None,
                                0,
                                token['direction'],
                                token['input'],
                                token['commentFactor'])

    return command


# This checks if the inputted command is formatted correctly and exists
def checkGivenCommand(command):
    lexedCommand = lexGivenCommand(command)
    command = parseGivenCommand(lexedCommand)
    sendCommandToServer(command)
