from tkinter import Tk, Text
from tkinter.font import Font
from tkinter.font import families
from queue import Queue
from time import sleep
from sys import exit
import GameState
import CommandController
import ServerConnect

# This is the list of all default command in the "Text" tag that modify the text
commandsToRemove = (
    "<Control-Key-h>",
    "<Meta-Key-Delete>",
    "<Meta-Key-BackSpace>",
    "<Meta-Key-d>",
    "<Meta-Key-b>",
    "<<Redo>>",
    "<<Undo>>",
    "<Control-Key-t>",
    "<Control-Key-o>",
    "<Control-Key-k>",
    "<Control-Key-d>",
    "<Key>",
    "<Key-Insert>",
    "<<PasteSelection>>",
    "<<Clear>>",
    "<<Paste>>",
    "<<Cut>>",
    "<Key-BackSpace>",
    "<Key-Delete>",
    "<Key-Return>",
    "<Control-Key-i>",
    "<Key-Tab>",
    "<Shift-Key-Tab>"
)


class ROText(Text):
    tagInit = False

    def init_tag(self):
        for key in self.bind_class("Text"):
            if key not in commandsToRemove:
                command = self.bind_class("Text", key)
                self.bind_class("ROText", key, command)
        ROText.tagInit = True

    def __init__(self, *args, **kwords):
        Text.__init__(self, *args, **kwords)
        if not ROText.tagInit:
            self.init_tag()

        bindTags = tuple(tag if tag != "Text" else "ROText" for tag in self.bindtags())
        self.bindtags(bindTags)


def handleCommand(event):
    if root.focus_get() != commandInputArea:
        if event.keysym != 'BackSpace':
            commandInputArea.focus()
            commandInputArea.insert('end', event.keysym)
    if event.keysym == 'Return':
        inputCommand = commandInputArea.get('1.0', 'end')
        inputCommand = inputCommand.strip('\n')
        if not inputCommand.isspace() and  \
           not inputCommand == '' and \
           not len(inputCommand) > 50:
            CommandController.checkGivenCommand(inputCommand)
        commandInputArea.delete('1.0', 'end')


def quitGame(event):
    root.destroy()
    ServerConnect.sendCommandToServer('disconnect')
    exit()


updateQueue = Queue()


def updateScreen():
    if not updateQueue.empty():
        screenUpdate = updateQueue.get()
        if 'staticFields' in screenUpdate or \
           'itemLocations' in screenUpdate or \
           'characterLocations' in screenUpdate:
            if GameState.outputArea1Function == 'areaDescriptionWindow':
                outputArea1.delete('1.0', 'end')
                outputArea1.insert('end', GameState.areaDescriptionWindowText)
                if outputArea1.bbox('end-1c') is not None:
                    outputArea1.see('end')
            if GameState.outputArea2Function == 'areaDescriptionWindow':
                outputArea2.delete('1.0', 'end')
                outputArea2.insert('end', GameState.areaDescriptionWindowText)
                if outputArea2.bbox('end-1c') is not None:
                    outputArea2.see('end')
            if GameState.outputArea3Function == 'areaDescriptionWindow':
                outputArea3.delete('1.0', 'end')
                outputArea3.insert('end', GameState.areaDescriptionWindowText)
                if outputArea3.bbox('end-1c') is not None:
                    outputArea3.see('end')
            if GameState.outputArea4Function == 'areaDescriptionWindow':
                outputArea4.delete('1.0', 'end')
                outputArea4.insert('end', GameState.areaDescriptionWindowText)
                if outputArea4.bbox('end-1c') is not None:
                    outputArea4.see('end')
        if 'staticFields' in screenUpdate:
            topWindow1.delete('1.0', 'end')
            topWindow1.insert('end', GameState.playerLocation['name'])
            if topWindow1.bbox('end-1c') is not None:
                topWindow1.see('end')
        if 'inventory' in screenUpdate:
            if GameState.outputArea1Function == 'inventoryWindow':
                outputArea1.delete('1.0', 'end')
                outputArea1.insert('end', GameState.inventoryWindowText)
                if outputArea1.bbox('end-1c') is not None:
                    outputArea1.see('end')
            if GameState.outputArea2Function == 'inventoryWindow':
                outputArea2.delete('1.0', 'end')
                outputArea2.insert('end', GameState.inventoryWindowText)
                if outputArea2.bbox('end-1c') is not None:
                    outputArea2.see('end')
            if GameState.outputArea3Function == 'inventoryWindow':
                outputArea3.delete('1.0', 'end')
                outputArea3.insert('end', GameState.inventoryWindowText)
                if outputArea3.bbox('end-1c') is not None:
                    outputArea3.see('end')
            if GameState.outputArea4Function == 'inventoryWindow':
                outputArea4.delete('1.0', 'end')
                outputArea4.insert('end', GameState.inventoryWindowText)
                if outputArea4.bbox('end-1c') is not None:
                    outputArea4.see('end')
    root.after(100, updateScreen)


def runMainloop():
    global root
    global gameFont
    global outputArea1
    global outputArea2
    global outputArea3
    global outputArea4
    global topWindow1
    global topWindow2
    global commandInputArea
    root = Tk(className='Text MMORPG')
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=0)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    root.rowconfigure(3, weight=0)

    gameFont = Font(family='times new roman', size=12)
    outputArea1 = ROText(root, cursor='arrow', bd=5, highlightthickness=0, relief='raised', font=gameFont, background='white')
    outputArea1.see('end')
    outputArea1.tag_add('normal', "1.0", "end")
    outputArea1.tag_config('normal', foreground="black")
    outputArea1.grid(row=1, column=0, sticky='nsew')
    chars = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    for char in chars:
        outputArea1.bind_all(char, handleCommand)
    outputArea1.bind_all('<Key-BackSpace>', handleCommand)
    outputArea1.bind_all('<Key-Return>', handleCommand)
    outputArea1.bind_all('<Control-Key-q>', quitGame)

    topWindow1 = ROText(root, cursor='arrow', bd=5, highlightthickness=0, relief='raised', height=1, font=gameFont, background='white')
    topWindow1.grid(row=0, column=0, sticky='nsew')
    topWindow1.see('end')
    topWindow1.tag_add("normal", "0.0", "end")
    topWindow1.tag_config("normal", foreground="black")

    topWindow2 = ROText(root, cursor='arrow', bd=5, highlightthickness=0, relief='raised', height=1, font=gameFont, background='white')
    topWindow2.grid(row=0, column=1, sticky='nsew')
    topWindow2.see('end')
    topWindow2.tag_add("normal", "0.0", "1000.1000")
    topWindow2.tag_config("normal", foreground="black")

    outputArea2 = ROText(root, cursor='arrow', bd=5, highlightthickness=0, relief='raised', font=gameFont, background='white')
    outputArea2.see('end')
    outputArea2.grid(row=1, column=1, sticky='nsew')
    outputArea2.tag_add("normal", "0.0", "1000.1000")
    outputArea2.tag_config("normal", foreground="black")

    outputArea3 = ROText(root, cursor='arrow', bd=5, highlightthickness=0, relief='raised', font=gameFont, background='white')
    outputArea3.see('end')
    outputArea3.grid(row=2, column=0, sticky='nsew')
    outputArea3.tag_add("normal", "0.0", "1000.1000")
    outputArea3.tag_config("normal", foreground="black")

    outputArea4 = ROText(root, cursor='arrow', bd=5, highlightthickness=0, relief='raised', font=gameFont, background='white')
    outputArea4.see('end')
    outputArea4.grid(row=2, column=1, sticky='nsew')
    outputArea4.tag_add("normal", "0.0", "1.1000")
    outputArea4.tag_config("normal", foreground="black")

    commandInputArea = Text(root, cursor='arrow', bd=5, highlightthickness=0, relief='raised', height=1, fg='black', font=gameFont, background='white')
    commandInputArea.grid(row=3, column=0, sticky='nsew', columnspan=2)

    root.after(0, updateScreen)
    root.mainloop()
