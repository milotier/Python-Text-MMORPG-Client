from __future__ import unicode_literals
import socket
import sys
from time import sleep
import CommandController
import GameState
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


# This defines the different objects that together will form vertical and horizontal splits
commandInputArea = TextArea(height=1, prompt=' >', style='class:input-field', multiline=False,wrap_lines=False, history=FileHistory('history.txt'))
horizontalLine = Window(height=1, char='-', style='class:line')
verticalLineExtra = Window(width=2, char='| ', style='class:line')
verticalLine = Window(width=1, char='|', style='class:line')
sideLine = Window(width=1, style='class:line')
outputArea1 = TextArea(style='class:output-field', height=20)
outputArea2 = TextArea(style='class:output-field', height=20)
outputArea3 = TextArea(style='class:output-field')
outputArea4 = TextArea(style='class:output-field')
corner = TextArea(multiline=False , height=1, width=1, text='+', read_only=True)

# This defines the different splits that together will form the layout of the application
outputAreas1And2 = HSplit([outputArea1, horizontalLine, outputArea3])
outputAreas3And4 = HSplit([outputArea2, horizontalLine, outputArea4])
horizontalDoubleCornerLine = VSplit([corner, horizontalLine, corner])
mainTextSplit = VSplit([verticalLine, outputAreas1And2, verticalLine, outputAreas3And4, verticalLine])
commandInputSplit = VSplit([verticalLine, commandInputArea, verticalLine])
sideSplit = VSplit([corner, horizontalLine, corner])
mainContainer = HSplit([sideSplit, horizontalDoubleCornerLine, mainTextSplit, horizontalDoubleCornerLine, commandInputSplit, sideSplit])

# This is ran everytime the user inputs a command via the commandInputArea object
def commandAcceptHandler(buff):
    CommandController.checkGivenCommand(commandInputArea.text)

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
def updateScreen():
    print(GameState.outputArea2Function)
    if GameState.outputArea1Function == 'commandOutputWindow':
        outputArea1.text = GameState.commandOutputWindowText
    if GameState.outputArea1Function == 'playerInfoWindow':
        outputArea1.text = GameState.playerInfoWindowText
    if GameState.outputArea1Function == 'chatWindow':
        outputArea1.text = GameState.chatWindowText
    if GameState.outputArea1Function == 'inventoryWindow':
        outputArea1.text = GameState.inventoryWindowText

    if GameState.outputArea2Function == 'commandOutputWindow':
        outputArea2.text = GameState.commandOutputWindowText
    if GameState.outputArea2Function == 'playerInfoWindow':
        outputArea2.text = GameState.playerInfoWindowText
    if GameState.outputArea2Function == 'chatWindow':
        outputArea2.text = GameState.chatWindowText
    if GameState.outputArea2Function == 'inventoryWindow':
        outputArea2.text = GameState.inventoryWindowText

    if GameState.outputArea3Function == 'commandOutputWindow':
        outputArea3.text = GameState.commandOutputWindowText
    if GameState.outputArea3Function == 'playerInfoWindow':
        outputArea3.text = GameState.playerInfoWindowText
    if GameState.outputArea3Function == 'chatWindow':
        outputArea3.text = GameState.chatWindowText
    if GameState.outputArea3Function == 'inventoryWindow':
        outputArea3.text = GameState.inventoryWindowText

    if GameState.outputArea4Function == 'commandOutputWindow':
        outputArea4.text = GameState.commandOutputWindowText
    if GameState.outputArea4Function == 'playerInfoWindow':
        outputArea4.text = GameState.playerInfoWindowText
    if GameState.outputArea4Function == 'chatWindow':
        outputArea4.text = GameState.chatWindowText
    if GameState.outputArea4Function == 'inventoryWindow':
        outputArea4.text = GameState.inventoryWindowText


# This function just runs the application      
def main():
    global app
    app.run()

    




    