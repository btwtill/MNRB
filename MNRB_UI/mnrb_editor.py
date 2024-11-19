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
        self._project_name = None
        self._mnrb_base_editor_path = None

        self.display_overlay = True

        self.initProject()
        self.initUI()

    @property
    def project_path(self): return self._project_path
    @project_path.setter
    def project_path(self, path):
        self._project_path = path
        self.project_name = os.path.basename(self._project_path)
        self._mnrb_base_editor_path = os.path.join(self._project_path, "mnrb_editor")

    @property
    def project_name(self): return self._project_name
    @project_name.setter
    def project_name(self, value):
        self._project_name = value

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
            self.onOpenProject()

        self.createEditorActions()
        self.setupMenuBar()
        
    def initTabs(self):
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self.setupNodeEditorTab()
        self.setupControlEditorTab()
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
        self.actionNewProject = QtWidgets.QAction('&New', self, shortcut='Ctrl+N', statusTip='create new project', triggered=self.onNewProjectFromMenuBar)
        self.actionOpenProject = QtWidgets.QAction('&Open', self, shortcut='Ctrl+O', statusTip='open a project', triggered=self.onOpenProjectFromMenuBar)
        self.actionSaveProjcet = QtWidgets.QAction('&Save', self, shortcut='Ctrl+S', statusTip='save project', triggered=self.onSaveProject)
        self.actionSaveProjcetAs = QtWidgets.QAction('Save&As', self, shortcut='Ctrl+Shift+S', statusTip='save project as', triggered=self.onSaveProjectAs)
        self.actionExit = QtWidgets.QAction('E&xit', self, shortcut='Ctrl+Q', statusTip='exit tool', triggered=self.close)

        self.actionLoadTemplate = QtWidgets.QAction('&Load Template', self, shortcut='Ctrl+L', statusTip='load template', triggered=self.onLoadNodeEditorFile)
        self.actionSaveTemplateAs = QtWidgets.QAction('Save &Template As', self, shortcut='Ctrl+Shift+Alt+S', statusTip='save template as', triggered=self.onSaveNodeEditorTemplateAs)
        self.actionClear = QtWidgets.QAction('&Clear', self, shortcut='Ctrl+Shift+C', statusTip='save template as', triggered=self.onClearNodeEditor)

        self.actionUndo = QtWidgets.QAction('&Undo', self, shortcut='Ctrl+Z', statusTip='undo last operation', triggered=self.onEditUndo)
        self.actionRedo = QtWidgets.QAction('&Redo', self, shortcut='Ctrl+Y', statusTip='redo last operation', triggered=self.onEditRedo)
        self.actionDelete = QtWidgets.QAction('&Delete', self, shortcut='Del', statusTip='delete currently Selected', triggered=self.onEditDelete)

        self.actionEditCopy = QtWidgets.QAction('&Copy', self, shortcut='Ctrl+C', statusTip='copy current selection', triggered=self.onEditCopy)
        self.actionEditCut = QtWidgets.QAction('&Cut', self, shortcut='Ctrl+X', statusTip='cut current selection', triggered=self.onEditCut)
        self.actionEditPaste = QtWidgets.QAction('&Paste', self, shortcut='Ctrl+V', statusTip='past current clipboard', triggered=self.onEditPaste)
    

    def setupMenuBar(self):
        menu_bar = self.menuBar()
        self.setupProjectMenu(menu_bar)
        self.setupNodeEditorMenu(menu_bar)
        self.setupEditMenu(menu_bar)

    def setupProjectMenu(self, menu_bar):
        self.project_menu = menu_bar.addMenu('&Project')

        self.project_menu.addAction(self.actionNewProject)
        self.project_menu.addSeparator()
        self.project_menu.addAction(self.actionOpenProject)
        self.project_menu.addSeparator()
        self.project_menu.addAction(self.actionSaveProjcet)
        self.project_menu.addAction(self.actionSaveProjcetAs)
        self.project_menu.addSeparator()
        self.project_menu.addAction(self.actionExit)

    def setupNodeEditorMenu(self, menu_bar):
        self.node_editor_menu = menu_bar.addMenu('&NodeEditor')

        self.node_editor_menu.addAction(self.actionLoadTemplate)
        self.node_editor_menu.addAction(self.actionSaveTemplateAs)
        self.node_editor_menu.addAction(self.actionClear)

    def setupEditMenu(self, menu_bar):
        self.edit_menu = menu_bar.addMenu('&Edit')

        self.edit_menu.addAction(self.actionUndo)
        self.edit_menu.addAction(self.actionRedo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.actionDelete)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.actionEditCopy)
        self.edit_menu.addAction(self.actionEditCut)
        self.edit_menu.addAction(self.actionEditPaste)
        
    def setupStatusBar(self):
        self.statusBar().showMessage('')
        self.statusMousePosition = QtWidgets.QLabel('')
        self.statusBar().addPermanentWidget(self.statusMousePosition)
        node_editor_tab= self.getNodeEditorTab()
        node_editor_tab.central_widget.view.scene_mouse_position_changed.connect(self.onSceneMousePositionChange) 

    def onNewProjectFromMenuBar(self):
        new_project_name_messageBox = QtWidgets.QMessageBox()

        new_project_name_messageBox.setWindowTitle("Please give your new MNRB Project a Title!")

        title_lineEdit = QtWidgets.QLineEdit()
        title_lineEdit.setPlaceholderText("Enter Title Here:")

        layout = new_project_name_messageBox.layout()
        layout.addWidget(title_lineEdit, layout.rowCount(), 0, 1, layout.columnCount())

        new_project_name_messageBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        result = new_project_name_messageBox.exec_()

        if result == QtWidgets.QMessageBox.Cancel:
            pass
        elif  result == QtWidgets.QMessageBox.Ok:
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

    def onOpenProjectFromMenuBar(self):
        if CLASS_DEBUG : print("MNRB_EDITOR:: -onOpenProject::  Start Opening project from Menu Bar",)

        directory_name = QtWidgets.QFileDialog.getExistingDirectoryUrl(self, "Open graph from file")
        if directory_name != '':
            directory_path = directory_name.toString().split("file:///")[1]
            if os.path.isdir(directory_path):
                self.project_path = directory_path
                self.onOpenProject()

    def onOpenProject(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onSaveProject:: Opening Project from Path:: ", self.project_path)

        self.initTabs()
        self.statusBar().showMessage(' Opened project from ' + self.project_path, 5000)
        try:
            self.getNodeEditorTab().onOpenFile(self._mnrb_base_editor_path)
        except Exception as e: print(e)

    def onSaveProject(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onSaveProject:: Start Saving Project")

        if self.project_path is not None:
            self.getNodeEditorTab().onSaveFile(os.path.join(self._mnrb_base_editor_path, self.project_name + "_graph"))
            self.statusBar().showMessage(' Saved Project to ' + self.project_path, 5000)
        else:
            self.onSaveProjectAs()

    def onSaveProjectAs(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onSaveAsProject:: Start Saving As Project")

        directory_name = QtWidgets.QFileDialog.getExistingDirectoryUrl(self, "Save Project To Location")
        if directory_name != '':
            directory_path = directory_name.toString().split("file:///")[1]
            if os.path.isdir(directory_path):
                self.project_path = directory_path

                self.statusBar().showMessage(' Saved Project As to ' + self.project_path, 5000)
                self.getNodeEditorTab().onSaveFile(os.path.join(self._mnrb_base_editor_path, self.project_name + "_graph"))

    def onLoadNodeEditorFile(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onLoadNodeEditorFile:: Load Node Editor File/Template")

        file_name, filter = QtWidgets.QFileDialog.getOpenFileName(self, "Open graph from file")
        if file_name == '':
            return
        if os.path.isfile(file_name):
            self.getNodeEditorTab().onOpenFile(file_name)
            self.statusBar().showMessage(' Successfully loaded Template from ' + file_name, 5000)
        
    def onSaveNodeEditorTemplateAs(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onSaveNodeEditorTemplateAs:: Save Node Editor File/Template As")
        file_name, filter = QtWidgets.QFileDialog.getSaveFileName(self, "Save Template to File")

        if file_name == '':
            return
        else:
            self.getNodeEditorTab().onSaveFile(file_name)
            self.statusBar().showMessage(' Successfully saved Template to ' + file_name, 5000)

    def onClearNodeEditor(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onClearNodeEditor:: Clearing Node Editor Space")

        self.getNodeEditorTab().clearScene()
        
    def onEditUndo(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onUndo:: Undo last operation!")
        try: 
            self.getNodeEditorTab().onUndo()
        except Exception as e: print(e)
    
    def onEditRedo(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onRedo:: Redo last operation!")
        try: 
            self.getNodeEditorTab().onRedo()
        except Exception as e: print(e)

    def onEditDelete(self):
        self.getNodeEditorTab().onDelete()

    def onEditCopy(self):
        self.getNodeEditorTab().onEditCopy()

    def onEditCut(self):
        self.getNodeEditorTab().onEditCut()

    def onEditPaste(self):
        self.getNodeEditorTab().onEditPaste()

    def onSceneMousePositionChange(self, x, y):
        self.statusMousePosition.setText("Scene Mouse Position: [%d %d]" % (x, y))

    def onPathItemDoubleClicked(self, item):
        path_items = item.text().split(" - ")
        self.project_path = path_items[1]
        self.onOpenProject()

    def loadProjectSettings(self):
        with open(self.project_settings_path, "r") as file:
            project_settings_raw = file.read()
            project_settings_json = json.loads(project_settings_raw)
        return project_settings_json

    def getNodeEditorTab(self):
        return self.tabs.widget(0).findChildren(QtWidgets.QMainWindow)[0]

    def getNodeEditorWidget(self):
        return self.tabs.widget(0).findChildren(QtWidgets.QMainWindow)[0].centralWidget()

    def getCurrentTabWidget(self):
        return self.tabs.currentWidget()

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