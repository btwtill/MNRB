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

        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self.setupNodeEditorTab()
        self.setupControlEditorTab()

    def setupNodeEditorTab(self):

        """Set up the first tab with an embedded main window containing dock widgets."""
        # Secondary main window within the first tab
        self.secondary_main_window = mnrb_NodeEditorTab()

        # First tab widget that will act as a container for the secondary main window
        first_tab_container = QtWidgets.QWidget()
        first_tab_layout = QtWidgets.QVBoxLayout(first_tab_container)

        # Add the secondary main window to the first tab's layout
        first_tab_layout.addWidget(self.secondary_main_window)
        
        # Add the first tab to the QTabWidget
        self.tabs.addTab(first_tab_container, "MNRB")


    def setupControlEditorTab(self):
        """Set up the second tab with a widget containing a box layout."""
        # Second tab central widget
        second_tab_widget = QtWidgets.QWidget()
        second_tab_layout = QtWidgets.QHBoxLayout(second_tab_widget)

        # Add widgets or controls in the box layout
        label1 = QtWidgets.QLabel("Box 1")
        label2 = QtWidgets.QLabel("Box 2")
        second_tab_layout.addWidget(label1)
        second_tab_layout.addWidget(label2)

        # Add the second tab to the QTabWidget
        self.tabs.addTab(second_tab_widget, "Tab 2")
    
    def on_button_clicked(self):
        """Handle button click event."""
        QtWidgets.QMessageBox.information(self, "Button Clicked", "You clicked the button!")

    def validateWorkingDirectory(self, directory):
        if DEBUG : print(directory)
        if DEBUG : print(os.path.basename(os.path.dirname(directory)))

        return not os.path.basename(os.path.dirname(directory)) == "default"