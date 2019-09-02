import CommandController
import GameState
from prompt_toolkit.layout.containers import Window, HSplit, VSplit
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.document import Document
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory

# Module which contains the prompt_toolkit application and it's eventloop


# This defines the different objects that
# together will form vertical and horizontal splits
commandInputArea = TextArea(height=1,
                            prompt='>',
                            style='class:input-field',
                            multiline=False, wrap_lines=False,
                            history=FileHistory('history.txt'))
horizontalLine = Window(height=1,
                        char='─',
                        style='class:line')
verticalLineTop = Window(width=1,
                         height=1,
                         char='│',
                         style='class:line')
verticalLine = Window(width=1,
                      char='│',
                      style='class:line')
verticalLine20 = Window(width=1,
                        height=20,
                        char='│',
                        style='class:line')
sideLine = Window(width=1,
                  style='class:line')
outputArea1 = TextArea(style='class:output-field',
                       height=20)
outputArea2 = TextArea(style='class:output-field',
                       height=20)
outputArea3 = TextArea(style='class:output-field')
outputArea4 = TextArea(style='class:output-field')
locationArea = TextArea(style='class:output-field',
                        height=1)
playerInfoArea = TextArea(style='class:output-field',
                          height=1)
descriptionArea = TextArea(style='class:output-field',
                           height=2)
topLeftCorner = Window(height=1,
                       width=1,
                       char='┌',
                       style='class:line')
topRightCorner = Window(height=1,
                        width=1,
                        char='┐',
                        style='class:line')
bottomLeftCorner = Window(height=1,
                          width=1,
                          char='└',
                          style='class:line')
bottomRightCorner = Window(height=1,
                           width=1,
                           char='┘',
                           style='class:line')
topMidCorner = Window(height=1,
                      width=1,
                      char='┬',
                      style='class:line')
bottomMidCorner = Window(height=1,
                         width=1,
                         char='┴',
                         style='class:line')
leftSideCorner = Window(height=1,
                        width=1,
                        char='├',
                        style='class:line')
rightSideCorner = Window(height=1,
                         width=1,
                         char='┤',
                         style='class:line')
midCorner = Window(height=1,
                   width=1,
                   char='┼',
                   style='class:line')

# This defines the different splits that
# together will form the layout of the application
outputAreas1And2 = HSplit([outputArea1,
                           horizontalLine,
                           outputArea3])
outputAreas3And4 = HSplit([outputArea2,
                           horizontalLine,
                           outputArea4])
commandInputLineTop = VSplit([leftSideCorner,
                              horizontalLine,
                              bottomMidCorner,
                              horizontalLine,
                              rightSideCorner])
leftVerticalLine = HSplit([verticalLine20,
                           leftSideCorner,
                           verticalLine])
midVerticalLine = HSplit([verticalLine20,
                          midCorner,
                          verticalLine])
rightVerticalLine = HSplit([verticalLine20,
                            rightSideCorner,
                            verticalLine])
mainTextSplit = VSplit([leftVerticalLine,
                        outputAreas1And2,
                        midVerticalLine,
                        outputAreas3And4,
                        rightVerticalLine])
commandInputSplit = VSplit([verticalLine,
                            commandInputArea,
                            verticalLine])
topLineSplit = VSplit([topLeftCorner,
                       horizontalLine,
                       topMidCorner,
                       horizontalLine,
                       topRightCorner])
topBottomLineMid = VSplit([bottomMidCorner,
                           horizontalLine,
                           topMidCorner,
                           horizontalLine,
                           bottomMidCorner])
topBottomLineSplit = VSplit([leftSideCorner,
                             horizontalLine,
                             midCorner,
                             horizontalLine,
                             rightSideCorner])
bottomLineSplit = VSplit([bottomLeftCorner,
                          horizontalLine,
                          bottomRightCorner])
topSplit = VSplit([verticalLineTop,
                  locationArea,
                  verticalLineTop,
                  playerInfoArea,
                  verticalLineTop])
mainContainer = HSplit([topLineSplit,
                        topSplit,
                        topBottomLineSplit,
                        mainTextSplit,
                        commandInputLineTop,
                        commandInputSplit,
                        bottomLineSplit])


# This is ran everytime the user inputs a command
# via the commandInputArea object
def commandAcceptHandler(buff):
    if commandInputArea.text.isspace() is not True and  \
       commandInputArea.text != '' and \
       not len(commandInputArea.text) > 50:
        command = '>' + commandInputArea.text
        GameState.screenUpdateQueue.put({'commandOutput': command, 'type': 'update'})
        CommandController.checkGivenCommand(commandInputArea.text)


# This binds the accept handler to the input area
commandInputArea.accept_handler = commandAcceptHandler

# Here the layout is made
layout = Layout(mainContainer, focused_element=commandInputArea)
kb = KeyBindings()

# This adds a keybind to the KeyBindings object
@kb.add('c-q')
def exit_(event):
    event.app.exit()


# This defines the style of the application
style = Style([
            ('output-field', 'bg:#000000 #ffffff'),
            ('input-field',  'bg:#000000 #ffffff'),
            ('line',         'bg:#000000 #ffffff'),
              ])

# Here the Application object is defined
global app
app = Application(layout=layout,
                  full_screen=True,
                  key_bindings=kb,
                  style=style,
                  mouse_support=True)


# This is the function that will update the screen
# with as parameter a list of all the changes to be made
def updateScreen():
    commandOutputWindowText = Document(
        text=GameState.commandOutputWindowText,
        cursor_position=len(GameState.commandOutputWindowText))
    skillWindowText = Document(
        text=GameState.skillWindowText,
        cursor_position=len(GameState.skillWindowText))
    chatWindowText = Document(
        text=GameState.chatWindowText,
        cursor_position=len(GameState.chatWindowText))
    inventoryWindowText = Document(
        text=GameState.inventoryWindowText,
        cursor_position=len(GameState.inventoryWindowText))
    areaDescriptionWindowText = Document(
        text=GameState.areaDescriptionWindowText,
        cursor_position=len(GameState.areaDescriptionWindowText))
    if GameState.outputArea1Function == 'commandOutputWindow':
        outputArea1.buffer.document = commandOutputWindowText
        outputArea1.text = GameState.commandOutputWindowText
    if GameState.outputArea1Function == 'skillWindow':
        outputArea1.buffer.document = skillWindowText
        outputArea1.text = GameState.skillWindowText
    if GameState.outputArea1Function == 'chatWindow':
        outputArea1.buffer.document = chatWindowText
        outputArea1.text = GameState.chatWindowText
    if GameState.outputArea1Function == 'inventoryWindow':
        outputArea1.buffer.document = inventoryWindowText
        outputArea1.text = GameState.inventoryWindowText
    if GameState.outputArea1Function == 'areaDescriptionWindow':
        outputArea1.buffer.document = areaDescriptionWindowText
        outputArea1.text = GameState.areaDescriptionWindowText

    if GameState.outputArea2Function == 'commandOutputWindow':
        outputArea2.buffer.document = commandOutputWindowText
        outputArea2.text = GameState.commandOutputWindowText
    if GameState.outputArea2Function == 'skillWindow':
        outputArea2.buffer.document = skillWindowText
        outputArea2.text = GameState.skillWindowText
    if GameState.outputArea2Function == 'chatWindow':
        outputArea2.buffer.document = chatWindowText
        outputArea2.text = GameState.chatWindowText
    if GameState.outputArea2Function == 'inventoryWindow':
        outputArea2.buffer.document = inventoryWindowText
        outputArea2.text = GameState.inventoryWindowText
    if GameState.outputArea2Function == 'areaDescriptionWindow':
        outputArea2.buffer.document = areaDescriptionWindowText
        outputArea2.text = GameState.areaDescriptionWindowText

    if GameState.outputArea3Function == 'commandOutputWindow':
        outputArea3.text = GameState.commandOutputWindowText
        outputArea3.buffer.document = commandOutputWindowText
    if GameState.outputArea3Function == 'skillWindow':
        outputArea3.text = GameState.skillWindowText
        outputArea3.buffer.document = skillWindowText
    if GameState.outputArea3Function == 'chatWindow':
        outputArea3.text = GameState.chatWindowText
        outputArea3.buffer.document = chatWindowText
    if GameState.outputArea3Function == 'inventoryWindow':
        outputArea3.text = GameState.inventoryWindowText
        outputArea3.buffer.document = inventoryWindowText
    if GameState.outputArea3Function == 'areaDescriptionWindow':
        outputArea3.buffer.document = areaDescriptionWindowText
        outputArea3.text = GameState.areaDescriptionWindowText

    if GameState.outputArea4Function == 'commandOutputWindow':
        outputArea4.text = GameState.commandOutputWindowText
        outputArea4.buffer.document = commandOutputWindowText
    if GameState.outputArea4Function == 'skillWindow':
        outputArea4.text = GameState.skillWindowText
        outputArea4.buffer.document = skillWindowText
    if GameState.outputArea4Function == 'chatWindow':
        outputArea4.text = GameState.chatWindowText
        outputArea4.buffer.document = chatWindowText
    if GameState.outputArea4Function == 'inventoryWindow':
        outputArea4.text = GameState.inventoryWindowText
        outputArea4.buffer.document = inventoryWindowText
    if GameState.outputArea4Function == 'areaDescriptionWindow':
        outputArea4.buffer.document = areaDescriptionWindowText
        outputArea4.text = GameState.areaDescriptionWindowText

    if 'name' in GameState.playerLocation:
        locationText = GameState.playerLocation['name']
        locationArea.buffer.document = Document(text=locationText)


# This function just runs the application
def main():
    global app
    app.run()
