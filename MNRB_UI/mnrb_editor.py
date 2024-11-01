import maya.cmds as cmds
import os
from PySide2 import QtWidgets, QtCore
from MNRB.MNRB_UI.mnrb_ui_utils import get_maya_window
from MNRB.MNRB_UI.mnrb_nodeEditorTab import mnrb_NodeEditorTab

DEBUG = True

class mnrb_Editor(QtWidgets.QMainWindow):
    def __init__(self, parent = get_maya_window()):
        super(mnrb_Editor, self).__init__(parent)

        self.workingDirectory = cmds.workspace(query=True, directory=True)
        self.isActiveProject = self.validateWorkingDirectory(self.workingDirectory)

        self.initUI()

    def initUI(self):

        self.setWindowTitle("mnrb Editor")
        self.setGeometry(300, 300, 800, 600)

        self.setupProjectOverlay()
        
        self.createEditorActions()
        self.setupMenuBar()
        self.setupStatusBar()

    def setupNodeEditorTab(self):

        #Set Up the NodeEditor Tab Object
        self.nodeEditorTabWindow = mnrb_NodeEditorTab()

        # Create a Widget acting as a container for the NodeEditor Window
        first_tab_container = QtWidgets.QWidget()
        first_tab_layout = QtWidgets.QVBoxLayout(first_tab_container)

        # Add the secondary main window to the first tab's layout
        first_tab_layout.addWidget(self.nodeEditorTabWindow)
        
        # Add the first tab to the QTabWidget
        self.tabs.addTab(first_tab_container, "MNRB")

    def setupControlEditorTab(self):
        
        # Second tab PlaceHolder Widget
        second_tab_widget = QtWidgets.QWidget()
        second_tab_layout = QtWidgets.QHBoxLayout(second_tab_widget)

        # Add widgets or controls in the box layout
        label1 = QtWidgets.QLabel("Box 1")
        label2 = QtWidgets.QLabel("Box 2")
        second_tab_layout.addWidget(label1)
        second_tab_layout.addWidget(label2)

        # Add the second tab to the QTabWidget
        self.tabs.addTab(second_tab_widget, "Tab 2")

    def setupProjectOverlay(self):

        self.overlay_Widget = QtWidgets.QWidget()

        self.outer_Layout = QtWidgets.QHBoxLayout()
        self.innerLayout = QtWidgets.QVBoxLayout()

        self.overlayNewActionButton = QtWidgets.QPushButton("New Project")
        self.overlayNewActionButton.clicked.connect(self.onNewProject)

        self.innerLayout.addWidget(self.overlayNewActionButton)
        self.innerLayout.setContentsMargins(60, 20, 60, 20)

        self.outer_Layout.addStretch(1)
        self.outer_Layout.addLayout(self.innerLayout)
        self.outer_Layout.addStretch(1)

        self.overlay_Widget.setLayout(self.outer_Layout)
        self.setCentralWidget(self.overlay_Widget)

    def createEditorActions(self):
        self.actionNew = QtWidgets.QAction('&New', self, shortcut='Ctrl+N', statusTip='Create New Project', triggered=self.onNewProject)
        self.actionOpen = QtWidgets.QAction('&Open', self, shortcut='Ctrl+O', statusTip='Open a Project', triggered=self.onOpenProject)

    def setupMenuBar(self):
        menuBar = self.menuBar()

        self.fileMenu = menuBar.addMenu('&File')
        self.fileMenu.addAction(self.actionNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actionOpen)

    def setupStatusBar(self):

        self.statusBar().showMessage('')
        self.statusMousePosition = QtWidgets.QLabel('')

    def onNewProject(self,):

        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self.setupNodeEditorTab()
        self.setupControlEditorTab()

    def onOpenProject(self):
        if DEBUG : print("Open a Project")

    def validateWorkingDirectory(self, directory):
        if DEBUG : print(directory)
        if DEBUG : print(os.path.basename(os.path.dirname(directory)))

        return not os.path.basename(os.path.dirname(directory)) == "default"