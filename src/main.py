# Imports
from threading import Thread

from src import connect
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import socket, time

# Classes
class ScrollLabel(QScrollArea):
    
    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)
        
    def text(self):
        return self.label.text()

class ServerRoom(QMainWindow):
    
    def __init__(self, password, port):
        # Init
        QMainWindow.__init__(self)
        
        # Set window properties
        self.setWindowTitle("Server room")
        
        uic.loadUi('./guis/ServerRoom.ui', self)
        
        # Set window icon
        app_icon = QtGui.QIcon()
        app_icon.addFile('icon.png', QSize(20, 20))
        self.setWindowIcon(app_icon)
        
        # Adding scrollbar
        self.Console = ScrollLabel(self)
        self.Console.setText("")
        self.Console.setGeometry(90, 372, 441, 131)
        
        # Properties
        self.server = connect.Server('', int(port), password, self)
        self.is_running = True
        self.startServerOrNot = False
        
        # Listen to triggers
        self.stopServer.clicked.connect(self.stopConnections)
        
        # Start the server
        Thread(target=self.server.start).start()
        
        # Update the gui
        Thread(target=self.update).start()
        
        self.show()
        
    def print_msg(self, msg):
        newline = "\n"
        
        if self.Console.text() == "":
            newline = ""
        
        self.Console.setText(self.Console.text() + newline + msg)
        
    def stopConnections(self):
        if self.startServerOrNot == False:
            self.server.stop()
            self.stopServer.setText("Start server")
            self.is_running = False
            self.startServerOrNot = True
        else:
            Thread(target=self.server.start).start()
            self.is_running = True
            Thread(target=self.update).start()
            self.stopServer.setText("Stop Server")
            self.startServerOrNot = False
        
    def update(self):
        while self.is_running:
            data = self.server.get_data()
            
            # Clear
            self.pilist.clear()
            
            # Update entries
            for name, value in data.items():
                entry = QTreeWidgetItem(self.pilist, [name, str(value['cpu_usage']), str(value['ram_usage']), str(value['temp'])])
            
            time.sleep(1)

class StartWindow(QMainWindow):
    
    def __init__(self, parent):
        # Init
        QMainWindow.__init__(self)
        
        # set window properties
        self.setWindowTitle("Fill in some info")
        
        uic.loadUi('./guis/ServerStart.ui', self)
        
        # Set window icon
        app_icon = QtGui.QIcon()
        app_icon.addFile('icon.png', QSize(20, 20))
        self.setWindowIcon(app_icon)
        
        self.parent = parent
        
        # Listen on some triggers
        self.startServerButton.clicked.connect(self.startServer)
        
    def startServer(self):
        # Get some values
        port = self.portTextBox.toPlainText()
        password = self.passwordTextBox.toPlainText()
        
        # Check if they're valid
        for char in port:
            if check_in_array(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], char) == False:
                QMessageBox.warning(self, "Invalid characters!", "Please input a valid port.")
                
                return
                        
        # Start the server
        self.server = ServerRoom(password, port)
        self.hide()
        self.parent.hide()
        

class MainWindow(QMainWindow):
    
    def __init__(self, app):
        # Init
        QMainWindow.__init__(self)
        
        # Init .ui file
        uic.loadUi('./guis/MainWindow.ui', self)
        
        # Set window properties
        self.setWindowTitle("Start a cave")
        
        # Set window icon
        app_icon = QtGui.QIcon()
        app_icon.addFile('icon.png', QSize(20, 20))
        self.setWindowIcon(app_icon)
        
        # Check for triggers
        self.startButton.clicked.connect(self.showStartWindow)
        
        self.show()
        
    def showStartWindow(self):
        self.startWindow = StartWindow(self)
        self.startWindow.show()
        

# Functions
def check_in_array(arr, key):
    for i in arr:
        if key == i:
            return True
        
    return False