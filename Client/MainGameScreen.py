from __future__ import unicode_literals
from queue import *
import socket
import sys
from time import sleep
from CommandController import checkGivenCommand
from prompt_toolkit.buffer import *
from prompt_toolkit.shortcuts.prompt import *
from prompt_toolkit.layout.containers import *
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.controls import *
from prompt_toolkit.layout.layout import *
from prompt_toolkit.formatted_text import *
from prompt_toolkit import *
from prompt_toolkit.key_binding import *
from prompt_toolkit.widgets import *
from prompt_toolkit.document import *
from prompt_toolkit.styles import *
from prompt_toolkit.history import *
from prompt_toolkit.output.base import *

# Module which contains the prompt_toolkit application and it's eventloop

# This defines the function of every of the four major output windows and the text they should contain
outputArea1Function = ''
outputArea2Function = ''
outputArea3Function = ''
outputArea4Function = ''
inventoryWindowText = ''
playerInfoWindowText = ''
commandOutputWindowText = ''
chatWindowText = ''

# This defines the queue object that will order the different updates of the screen as FIFO (FirstInFirstOut)
screenUpdateQueue = Queue()

# This defines the different objects that together will form vertical and horizontal splits
commandInputArea = TextArea(height=1, prompt=' >', style='class:input-field', multiline=False,wrap_lines=False, history=FileHistory('history.txt'))
horizontalLine = Window(height=1, char='-', style='class:line')
verticalLineExtra = Window(width=2, char='| ', style='class:line')
verticalLine = Window(width=1, char='|', style='class:line')
sideLine = Window(width=1, style='class:line')
outputArea1 = TextArea(style='class:output-field', height=20)
outputArea2 = TextArea(style='class:output-field')
outputArea3 = TextArea(style='class:output-field', height=20)
outputArea4 = TextArea(style='class:output-field')
corner = TextArea(multiline=False , height=1, width=1, text='+', read_only=True)

# This defines the different splits that together will form the layout of the application
outputAreas1And2 = HSplit([outputArea1, horizontalLine, outputArea2])
outputAreas3And4 = HSplit([outputArea3, horizontalLine, outputArea4])
horizontalDoubleCornerLine = VSplit([corner, horizontalLine, corner])
mainTextSplit = VSplit([verticalLine, outputAreas1And2, verticalLine, outputAreas3And4, verticalLine])
commandInputSplit = VSplit([verticalLine, commandInputArea, verticalLine])
sideSplit = VSplit([corner, horizontalLine, corner])
mainContainer = HSplit([sideSplit, horizontalDoubleCornerLine, mainTextSplit, horizontalDoubleCornerLine, commandInputSplit, sideSplit])

# This is ran everytime the user inputs a command via the commandInputArea object
def commandAcceptHandler(buff):
    checkGivenCommand(commandInputArea.text)

# This binds the accept handler to the input area
commandInputArea.accept_handler = commandAcceptHandler

# Here the layout is made
layout = Layout(mainContainer, focused_element = commandInputArea)
kb = KeyBindings()

# This adds a keybind to the KeyBindings object
@kb.add('c-q')
def exit_(event):
    event.app.exit()

# This defines the style of the application
style = Style([
            ('output-field', 'bg:#000000 #ffffff'),
            ('input-field', 'bg:#000000 #ffffff'),
            ('line',        '#ffffff'),
              ])

# Here the Application object is defined
global app
app = Application(layout=layout, full_screen=True, key_bindings=kb, style=style, mouse_support=True)

# This is the function that will update the screen with as parameter a list of all the changes to be made
def updateScreen(changeList):
    global app
    if changeList == 'server went down':
        try:
            app.exit()
            sleep(0.5)
            print('\n\nThe server is down at the moment. Please wait and come back later.\n\n')
        except:
            pass

    global playerInfoWindowText
    global commandOutputWindowText
    global inventoryWindowText
    global chatWindowText
    global outputArea1Function
    global outputArea2Function
    global outputArea3Function
    global outputArea4Function
    for change in changeList:
        if change[0] == 'playerInfoWindowText':
            playerInfoWindowText = change[1]
            if outputArea1Function == 'playerInfoWindow':
                outputArea1.text = playerInfoWindowText
            elif outputArea2Function == 'playerInfoWindow':
                outputArea2.text = playerInfoWindowText
            elif outputArea3Function == 'playerInfoWindow':
                outputArea3.text = playerInfoWindowText
            elif outputArea4Function == 'playerInfoWindow':
                outputArea4.text = playerInfoWindowText
        if change[0] == 'commandOutputWindowText':
            commandOutputWindowText = change[1]
            if outputArea1Function == 'commandOutputWindow':
                outputArea1.text = commandOutputWindowText
            elif outputArea2Function == 'commandOutputWindow':
                outputArea2.text = commandOutputWindowText
            elif outputArea3Function == 'commandOutputWindow':
                outputArea3.text = commandOutputWindowText
            elif outputArea4Function == 'commandOutputWindow':
                outputArea4.text = commandOutputWindowText
        if change[0] == 'inventoryWindowText':
            inventoryWindowText = change[1]
            if outputArea1Function == 'inventoryWindow':
                outputArea1.text = inventoryWindowText
            elif outputArea2Function == 'inventoryWindow':
                outputArea2.text = inventoryWindowText
            elif outputArea3Function == 'inventoryWindow':
                outputArea3.text = inventoryWindowText
            elif outputArea4Function == 'inventoryWindow':
                outputArea4.text = inventoryWindowText
        if change[0] == 'chatWindowText':
            chatWindowText = change[1]
            if outputArea1Function == 'chatWindow':
                outputArea1.text = chatWindowText
            elif outputArea2Function == 'chatWindow':
                outputArea2.text = chatWindowText
            elif outputArea3Function == 'chatWindow':
                outputArea3.text = chatWindowText
            elif outputArea4Function == 'chatWindow':
                outputArea4.text = chatWindowText

        if change[0] == 'outputArea1Function':
            if change[1] == 'playerInfoWindow':
                outputArea1Function = 'playerInfoWindow'
                outputArea1.text = playerInfoWindowText
            if change[1] == 'commandOutputWindow':
                outputArea1Function = 'commandOutputWindow'
                outputArea1.text = commandOutputWindowText
            if change[1] == 'inventoryWindow':
                outputArea1Function = 'inventoryWindow'
                outputArea1.text = inventoryWindowText
            if change[1] == 'chatWindow':
                outputArea1Function = 'chatWindow'
                outputArea1.text = chatWindowText
        elif change[0] == 'outputArea2Function':
            if change[1] == 'playerInfoWindow':
                outputArea2Function = 'playerInfoWindow'
                outputArea2.text = playerInfoWindowText
            if change[1] == 'commandOutputWindow':
                outputArea2Function = 'commandOutputWindow'
                outputArea2.text = commandOutputWindowText
            if change[1] == 'inventoryWindow':
                outputArea2Function = 'inventoryWindow'
                outputArea2.text = inventoryWindowText
            if change[1] == 'chatWindow':
                outputArea2Function = 'chatWindow'
                outputArea2.text = chatWindowText
        elif change[0] == 'outputArea3Function':
            if change[1] == 'playerInfoWindow':
                outputArea3Function = 'playerInfoWindow'
                outputArea3.text = playerInfoWindowText
            if change[1] == 'commandOutputWindow':
                outputArea3Function = 'commandOutputWindow'
                outputArea3.text = commandOutputWindowText
            if change[1] == 'inventoryWindow':
                outputArea3Function = 'inventoryWindow'
                outputArea3.text = inventoryWindowText
            if change[1] == 'chatWindow':
                outputArea3Function = 'chatWindow'
                outputArea3.text = chatWindowText
        elif change[0] == 'outputArea4Function':
            if change[1] == 'playerInfoWindow':
                outputArea4Function = 'playerInfoWindow'
                outputArea4.text = playerInfoWindowText
            if change[1] == 'commandOutputWindow':
                outputArea4Function = 'commandOutputWindow'
                outputArea4.text = commandOutputWindowText
            if change[1] == 'inventoryWindow':
                outputArea4Function = 'inventoryWindow'
                outputArea4.text = inventoryWindowText
            if change[1] == 'chatWindow':
                outputArea4Function = 'chatWindow'
                outputArea4.text = chatWindowText

# This function just runs the application      
def main():
    global app
    app.run()

    




    