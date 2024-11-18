import os
import json
import maya.cmds as cmds # type: ignore
from PySide2 import QtWidgets # type: ignore
from PySide2.QtCore import QFile #type:  ignore 
from MNRB.MNRB_UI.mnrb_ui_utils import getMayaWindow # type: ignore
from MNRB.MNRB_UI.mnrb_nodeEditorTab import mnrb_NodeEditorTab # type: ignore

CLASS_DEBUG = True

class mnrb_Editor(QtWidgets.QMainWindow):
    def __init__(self, parent = getMayaWindow()):
        super(mnrb_Editor, self).__init__(parent)

        self.project_settings_path = os.path.join(os.path.dirname(__file__), "project_settings.json")
        self.project_settings = self.loadProjectSettings()

        self.working_directory = cmds.workspace(query=True, directory=True)
        self.is_active_project = self.validateWorkingDirectory(self.working_directory)

        self.mnrb_path = os.path.join(self.working_directory, self.project_settings['ProjectSubPath'], "MNRB")

        self._project_path = None
        self._mnrb_base_editor_path = None

        self.display_overlay = True

        self.initProject()
        self.initUI()

    @property
    def project_path(self): return self._project_path
    @project_path.setter
    def project_path(self, path):
        self._project_path = path
        self._mnrb_base_editor_path = os.path.join(self._project_path, "mnrb_editor")


    def initProject(self):

        #Check if in the Current Working Directory + The Defined Subfolder for the ProjectDirectory is an MNRB Folder and how many Projects are in it
        if os.path.isdir(self.mnrb_path):
            if CLASS_DEBUG: print("MNRB_EDITOR:: --initProject:: MNRB Directory found in current working Directory!")
            projects = os.listdir(self.mnrb_path)
            if CLASS_DEBUG: print("MNRB_EDITR:: --initProject:: MNRB Content:: ", projects)

            if len(projects) == 1 and os.path.isdir(os.path.join(self.mnrb_path, projects[0])):
                if CLASS_DEBUG: print("MNRB_EDITR:: --initProject:: found Only One MNRB Project, proceed opening Project Directly")
                self.project_path = os.path.join(self.mnrb_path, projects[0])
                self.display_overlay = False
            else:
                if CLASS_DEBUG: print("MNRB_EDITR:: --initProject:: Multiple or No Projcets found, Display Overlay")
                self.display_overlay = True
        else:
            if CLASS_DEBUG: 
                print("MNRB_EDITOR:: --initProject:: No MNRB Directory Found. ")
                os.mkdir(self.mnrb_path)
                print("MNRB_EDITOR:: --initProject:: Create MNRB Directory at path and Display Overlay")
                self.display_overlay = True

    def initUI(self):

        self.setWindowTitle("mnrb Editor")
        self.setGeometry(200, 200, 1200, 700)

        if self.display_overlay:
            self.setupProjectOverlay()
        else:
            self.onOpenProject(self.project_path)

        self.createEditorActions()
        self.setupMenuBar()
        self.setupStatusBar()

    def initTabs(self):

        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self.setupNodeEditorTab()
        self.setupControlEditorTab()

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
        self.innerLayout.addStretch()

        self.project_name_lineEdit = QtWidgets.QLineEdit()
        self.project_name_lineEdit.setPlaceholderText("Enter Project Name:")

        self.overlayNewActionButton = QtWidgets.QPushButton("New Project")
        self.overlayNewActionButton.clicked.connect(lambda: self.onNewProject(self.project_name_lineEdit.text()))

        current_workspace_projects = os.listdir(self.mnrb_path)

        self.current_workspace_projects_list = QtWidgets.QListWidget()

        for item in current_workspace_projects:
            new_poject_list_item = QtWidgets.QListWidgetItem()
            new_poject_list_item.setText(item + " - " + os.path.join(self.mnrb_path, item))
            self.current_workspace_projects_list.addItem(new_poject_list_item)

        self.current_workspace_projects_list.itemDoubleClicked.connect(self.onPathItemDoubleClicked)

        self.innerLayout.addWidget(self.project_name_lineEdit)
        self.innerLayout.addWidget(self.overlayNewActionButton)
        self.innerLayout.addWidget(self.current_workspace_projects_list)
        self.innerLayout.setContentsMargins(60, 20, 60, 20)

        self.innerLayout.addStretch()
        self.outer_Layout.addStretch(1)
        self.outer_Layout.addLayout(self.innerLayout)
        self.outer_Layout.addStretch(1)

        self.overlay_Widget.setLayout(self.outer_Layout)
        self.setCentralWidget(self.overlay_Widget)


    def createEditorActions(self):
        self.actionNew = QtWidgets.QAction('&New', self, shortcut='Ctrl+N', statusTip='Create New Project', triggered=self.onNewProjectFromMenuBar)
        self.actionOpen = QtWidgets.QAction('&Open', self, shortcut='Ctrl+O', statusTip='Open a Project', triggered=self.onOpenProject)
        self.actionSave = QtWidgets.QAction('&Save', self, shortcut='Ctrl+S', statusTip='Save Project', triggered=self.onSaveProject)
        self.actionSaveAs = QtWidgets.QAction('Save&As', self, shortcut='Ctrl+S', statusTip='Save Project As', triggered=self.onSaveProjectAs)

    def setupMenuBar(self):
        menuBar = self.menuBar()

        self.fileMenu = menuBar.addMenu('&File')
        self.fileMenu.addAction(self.actionNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actionOpen)

    def setupStatusBar(self):

        self.statusBar().showMessage('')
        self.statusMousePosition = QtWidgets.QLabel('')

    def onNewProjectFromMenuBar(self):
        new_project_name_messageBox = QtWidgets.QMessageBox()

        new_project_name_messageBox.setWindowTitle("Please give your new MNRB Project a Title!")

        title_lineEdit = QtWidgets.QLineEdit()
        title_lineEdit.setPlaceholderText("Enter Title Here:")

        layout = new_project_name_messageBox.layout()
        layout.addWidget(title_lineEdit, layout.rowCount(), 0, 1, layout.columnCount())

        result = new_project_name_messageBox.exec_()

        if  result == QtWidgets.QMessageBox.Ok:
            self.onNewProject(title_lineEdit.text())
            
    def onNewProject(self, name):
        if self.validateProjectName(name):

            #create Project
            self.project_path = os.path.join(self.mnrb_path, name)

            os.mkdir(self.project_path)

            #creating The Projcet Hirarchy
            os.mkdir(self._mnrb_base_editor_path)

            self.initTabs()
        else:
            warningBox = QtWidgets.QMessageBox()
            warningBox.setWindowTitle("The Name is Invalid")
            warningBox.setText("The name is either none, already taken or contains illigal symbols \n Please Change the name of your Project!")
            warningBox.setIcon(QtWidgets.QMessageBox.Critical)

            warningBox.exec_()      

    def onOpenProject(self, path=None):
        if CLASS_DEBUG : print("MNRB_EDITOR:: -onOpenProject:: Start opening a Project from path:: ", path)

        self.initTabs()

    def onSaveProject(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onSaveProject:: Start Saving Project")

    def onSaveProjectAs(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onSaveProject:: Start Saving Project")

    def onPathItemDoubleClicked(self, item):
        path_items = item.text().split(" - ")
        self.onOpenProject(path_items[1])

    def loadProjectSettings(self):
        with open(self.project_settings_path, "r") as file:
            project_settings_raw = file.read()
            project_settings_json = json.loads(project_settings_raw)
        return project_settings_json

    def getNodeEditorWidget(self):
        return self.tabs.widget(0)

    def validateProjectName(self, name):

        mnrb_projects = os.listdir(self.mnrb_path)
        if name == "": 
            return False
        elif name in mnrb_projects :
            return False
        else:
            return True
      

    def validateWorkingDirectory(self, directory):
        if CLASS_DEBUG : print("MNRB_EDITOR:: -validateWorkingDirectory:: Full Directory Path: ", directory)
        if CLASS_DEBUG : print("MNRB_EDITOR:: -validateWorkingDirectory:: WorkingDirectoryName: ", os.path.basename(os.path.dirname(directory)))

        return not os.path.basename(os.path.dirname(directory)) == "default"