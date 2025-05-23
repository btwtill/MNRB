import os
import json
import maya.cmds as cmds # type: ignore
from PySide2 import QtWidgets # type: ignore
from PySide2.QtCore import Qt, QFile, QSettings, QPoint, QSize, QTimer #type:  ignore 
from MNRB.MNRB_UI.mnrb_ui_utils import getMayaWindow # type: ignore
from MNRB.MNRB_UI.mnrb_nodeEditorTab import mnrb_NodeEditorTab # type: ignore
from MNRB.MNRB_UI.preferences_UI.preferences_widget import MNRBPreferences #type: ignore
from MNRB.MNRB_UI.mnrb_skinningEditorTab import mnrb_SkinningEditorTab #type: ignore

CLASS_DEBUG = True

class mnrb_Editor(QtWidgets.QMainWindow):
    def __init__(self, parent = getMayaWindow()):
        super(mnrb_Editor, self).__init__(parent)

        self.project_settings_path = os.path.join(os.path.dirname(__file__), "project_settings.json")
        self.project_settings = self.loadProjectSettings()

        self.working_directory = cmds.workspace(query=True, rootDirectory=True)
        self.is_active_project = self.validateWorkingDirectory(self.working_directory)

        self.mnrb_path = os.path.join(self.working_directory, self.project_settings['ProjectSubPath'], "MNRB")

        self._project_path = None
        self._project_name = None
        self.mnrb_base_editor_path_name = "mnrb_editor"
        self.mnrb_base_editor_path = None
        self.mnrb_skinning_editor_path_name = "mnrb_skinning_editor"
        self.mnrb_skinning_editor_path = None

        self.display_overlay = True

        self.initProject()
        self.initTabs()
        self.initUI()
       
    @property
    def project_path(self): return self._project_path
    @project_path.setter
    def project_path(self, path):
        self._project_path = path
        self.project_name = os.path.basename(self._project_path)
        
        self.mnrb_base_editor_path = os.path.join(self._project_path, self.mnrb_base_editor_path_name)
        self.mnrb_skinning_editor_path = os.path.join(self._project_path, self.mnrb_skinning_editor_path_name)

    @property
    def project_name(self): return self._project_name
    @project_name.setter
    def project_name(self, value):
        self._project_name = value
        self.setTitleText()

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
        self.setGeometry(200, 200, 1200, 700)
        self.readSettings()

        self.createEditorActions()
        self.setupMenuBar()
        
    def initTabs(self):
        self.tabs = QtWidgets.QTabWidget()

        self.setupNodeEditorTab()
        self.setupSkinEditorTab()
        self.setupControlEditorTab()
        self.setupStatusBar()

        self.getNodeEditorTab().central_widget.scene.connectHasBeenModifiedListenerCallback(self.setTitleText)
        
        if self.display_overlay:
            self.setupProjectOverlay()
        else:
            self.display_overlay = True
            self.onOpenProject()

        self.getNodeEditorTab().central_widget.scene.history.connectHistoryModifiedListenersCallback(self.updateEditMenu)
        self.getNodeEditorTab().central_widget.scene.connectBuildHasBeenTriggeredListenerCallback(self.getSkinningEditorTab().pullDeformerDictFromNodeEditor)

        self.tabs.currentChanged.connect(self.updateCurrentTab)

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

    def setupSkinEditorTab(self):
        # Skining tab PlaceHolder Widget
        self.skinningEditorTabWindow = mnrb_SkinningEditorTab(self.nodeEditorTabWindow)

        second_tab_container = QtWidgets.QWidget()
        second_tab_layout = QtWidgets.QVBoxLayout(second_tab_container)
        second_tab_container.is_tab_widget = True

        second_tab_layout.addWidget(self.skinningEditorTabWindow)

        # Add the second tab to the QTabWidget
        self.tabs.addTab(second_tab_container, "Skin")

    def setupControlEditorTab(self):
        # Third tab PlaceHolder Widget
        second_tab_widget = QtWidgets.QWidget()
        second_tab_layout = QtWidgets.QHBoxLayout(second_tab_widget)

        second_tab_widget.is_tab_widget = True

        # Add widgets or controls in the box layout
        label1 = QtWidgets.QLabel("Box 1")
        label2 = QtWidgets.QLabel("Box 2")
        second_tab_layout.addWidget(label1)
        second_tab_layout.addWidget(label2)

        # Add the second tab to the QTabWidget
        self.tabs.addTab(second_tab_widget, "Tab 2")

    def setupProjectOverlay(self):
        #create and fill the widget that is displayed when there are multiple projects or no project found in the workdirectory
        self.overlay_Widget = QtWidgets.QWidget()

        self.outer_Layout = QtWidgets.QHBoxLayout()
        self.innerLayout = QtWidgets.QVBoxLayout()
        self.innerLayout.addStretch()

        self.project_name_lineEdit = QtWidgets.QLineEdit()
        self.project_name_lineEdit.setPlaceholderText("Enter Project Name:")

        self.overlayNewActionButton = QtWidgets.QPushButton("New Project")
        self.overlayNewActionButton.clicked.connect(lambda: self.onNewProject(self.project_name_lineEdit.text()))

        self.overlayOpenActionButton = QtWidgets.QPushButton("Open Project")
        self.overlayOpenActionButton.clicked.connect(self.onOverlayOpenProject)
        self.overlayOpenActionButton.setEnabled(False)

        current_workspace_projects = os.listdir(self.mnrb_path)

        self.current_projects_list_label = QtWidgets.QLabel("Projects found in current workdirectory: ")

        self.current_workspace_projects_list = QtWidgets.QListWidget()
        self.current_workspace_projects_list.setFixedWidth(400)

        for item in current_workspace_projects:
            new_poject_list_item = QtWidgets.QListWidgetItem()
            new_poject_list_item.setText(item + " - " + os.path.join(self.mnrb_path, item))
            self.current_workspace_projects_list.addItem(new_poject_list_item)

        self.current_workspace_projects_list.itemDoubleClicked.connect(self.onPathItemDoubleClicked)
        self.current_workspace_projects_list.itemPressed.connect(self.onPathItemPressed)

        self.overlayOpenFromDirectoryActionButton = QtWidgets.QPushButton("Open From...")
        self.overlayOpenFromDirectoryActionButton.clicked.connect(self.onOpenProjectFromMenuBar)

        overlay_title = QtWidgets.QLabel("MNRB - Editor")
        overlay_title.setAlignment(Qt.AlignCenter)
        overlay_title.setStyleSheet("font-size: 36px; font-weight: bold;")

        initial_spacer = QtWidgets.QWidget()
        initial_spacer.setFixedHeight(50)

        self.innerLayout.addWidget(initial_spacer)
        self.innerLayout.addWidget(overlay_title)
        self.innerLayout.addWidget(initial_spacer)
        self.innerLayout.addWidget(self.project_name_lineEdit)
        self.innerLayout.addWidget(self.overlayNewActionButton)
        self.innerLayout.addWidget(self.overlayOpenActionButton)
        self.innerLayout.addWidget(self.current_projects_list_label)
        self.innerLayout.addWidget(self.current_workspace_projects_list)
        self.innerLayout.addWidget(self.overlayOpenFromDirectoryActionButton)
        self.innerLayout.setContentsMargins(60, 20, 60, 20)

        self.innerLayout.addStretch()
        self.outer_Layout.addStretch(1)
        self.outer_Layout.addLayout(self.innerLayout)
        self.outer_Layout.addStretch(1)

        self.overlay_Widget.setLayout(self.outer_Layout)
        self.setCentralWidget(self.overlay_Widget)
        
    def createEditorActions(self):
        self.action_new_project = QtWidgets.QAction('&New', self, shortcut='Ctrl+N', statusTip='create new project', triggered=self.onNewProjectFromMenuBar)
        self.action_open_project = QtWidgets.QAction('&Open', self, shortcut='Ctrl+O', statusTip='open a project', triggered=self.onOpenProjectFromMenuBar)
        self.action_save_project = QtWidgets.QAction('&Save', self, shortcut='Ctrl+S', statusTip='save project', triggered=self.onSaveProject)
        #self.action_save_project_as = QtWidgets.QAction('Save&As', self, shortcut='Ctrl+Shift+S', statusTip='save project as', triggered=self.onSaveProjectAs)
        self.action_exit = QtWidgets.QAction('E&xit', self, shortcut='Ctrl+Q', statusTip='exit tool', triggered=self.close)

        self.action_load_template = QtWidgets.QAction('&Load Template', self, shortcut='Ctrl+L', statusTip='load template', triggered=self.onLoadNodeEditorFile)
        self.actionSaveTemplateAs = QtWidgets.QAction('Save &Template As', self, shortcut='Ctrl+Shift+Alt+S', statusTip='save template as', triggered=self.onSaveNodeEditorTemplateAs)
        self.action_clear = QtWidgets.QAction('&Clear', self, shortcut='Ctrl+Shift+C', statusTip='save template as', triggered=self.onClearNodeEditor)
        self.action_align_on_x = QtWidgets.QAction('Align&X', self, shortcut = 'Alt+X', statusTip = 'align nodes vertivally', triggered=self.onNodeEditorAlignX)
        self.action_align_on_y = QtWidgets.QAction('Align&Y', self, shortcut = 'Alt+Y', statusTip = 'align nodes horizontally', triggered=self.onNodeEditorAlignY)
        self.action_mirror_Node = QtWidgets.QAction('Mirror Node', self, shortcut = 'Alt+M', statusTip = 'mirror node', triggered=self.onNodeEditorMirrorNode)

        self.action_undo = QtWidgets.QAction('&Undo', self, shortcut='Ctrl+Z', statusTip='undo last operation', triggered=self.onEditUndo)
        self.action_redo = QtWidgets.QAction('&Redo', self, shortcut='Ctrl+Y', statusTip='redo last operation', triggered=self.onEditRedo)
        self.action_delete = QtWidgets.QAction('&Delete', self, shortcut='Del', statusTip='delete currently Selected', triggered=self.onEditDelete)

        self.action_edit_preferences = QtWidgets.QAction('&Preferences', self, statusTip='open Preferences', triggered=self.onOpenPreferences)

        self.action_edit_copy = QtWidgets.QAction('&Copy', self, shortcut='Ctrl+C', statusTip='copy current selection', triggered=self.onEditCopy)
        self.action_edit_cut = QtWidgets.QAction('&Cut', self, shortcut='Ctrl+X', statusTip='cut current selection', triggered=self.onEditCut)
        self.action_edit_paste = QtWidgets.QAction('&Paste', self, shortcut='Ctrl+V', statusTip='past current clipboard', triggered=self.onEditPaste)

        self.action_about = QtWidgets.QAction('&About', self, shortcut = '', statusTip='information about MNRB', triggered=self.onAbout)
    
    def setupMenuBar(self):
        menu_bar = self.menuBar()
        self.setupProjectMenu(menu_bar)
        self.setupEditMenu(menu_bar)
        self.setupNodeEditorMenu(menu_bar)
        self.setupAboutMenu(menu_bar)
        
    def setupProjectMenu(self, menu_bar):
        self.project_menu = menu_bar.addMenu('&Project')

        self.project_menu.addAction(self.action_new_project)
        self.project_menu.addSeparator()
        self.project_menu.addAction(self.action_open_project)
        self.project_menu.addSeparator()
        self.project_menu.addAction(self.action_save_project)
        #self.project_menu.addAction(self.action_save_project_as)
        self.project_menu.addSeparator()
        self.project_menu.addAction(self.action_exit)

        self.project_menu.aboutToShow.connect(self.updateProjectMenu)

    def setupEditMenu(self, menu_bar):
        self.edit_menu = menu_bar.addMenu('&Edit')

        self.edit_menu.addAction(self.action_undo)
        self.edit_menu.addAction(self.action_redo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_delete)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_edit_copy)
        self.edit_menu.addAction(self.action_edit_cut)
        self.edit_menu.addAction(self.action_edit_paste)

        self.edit_menu.addSeparator()

        self.edit_menu.addAction(self.action_edit_preferences)

        self.edit_menu.aboutToShow.connect(self.updateEditMenu)

    def setupNodeEditorMenu(self, menu_bar):
        self.node_editor_menu = menu_bar.addMenu('&MNRB')

        self.node_editor_menu.addAction(self.action_load_template)
        self.node_editor_menu.addAction(self.actionSaveTemplateAs)
        self.node_editor_menu.addAction(self.action_clear)

        self.node_editor_menu.addSeparator()

        self.action_nodes_list_dock_visibility = self.node_editor_menu.addAction("Nodes List")
        self.action_nodes_list_dock_visibility.setCheckable(True)
        self.action_nodes_list_dock_visibility.triggered.connect(self.onNodeListDockWidget)
        
        self.action_nodes_properties_dock_visibility = self.node_editor_menu.addAction("Node Properties")
        self.action_nodes_properties_dock_visibility.setCheckable(True)
        self.action_nodes_properties_dock_visibility.triggered.connect(self.onPropertiesDockWidget)

        self.node_editor_menu.addSeparator()

        self.node_editor_menu.addAction(self.action_align_on_x)
        self.node_editor_menu.addAction(self.action_align_on_y)
        self.node_editor_menu.addAction(self.action_mirror_Node)

        self.node_editor_menu.aboutToShow.connect(self.updateNodeEditorMenu)
    
    def setupAboutMenu(self, menu_bar):
        self.about_menu = menu_bar.addMenu('&About')

        self.about_menu.addAction(self.action_about)

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
        if self.projectNeedsSaving():
            if self.validateProjectName(name):

                #create Project
                self.project_path = os.path.join(self.mnrb_path, name)
                os.mkdir(self.project_path)

                #creating The Project Hirarchy
                if self.mnrb_base_editor_path:
                    os.mkdir(self.mnrb_base_editor_path)
                if self.mnrb_skinning_editor_path:
                    os.mkdir(self.mnrb_skinning_editor_path)

                if self.display_overlay:
                    self.setCentralWidget(self.tabs)

                self.display_overlay = False

                self.getNodeEditorTab().onNewFile()

            else:
                warningBox = QtWidgets.QMessageBox()
                warningBox.setWindowTitle("The Name is Invalid")
                warningBox.setText("The name is either none, already taken or contains illigal symbols \n Please Change the name of your Project!")
                warningBox.setIcon(QtWidgets.QMessageBox.Critical)

                warningBox.exec_()

    def onOpenProjectFromMenuBar(self):
        if CLASS_DEBUG : print("MNRB_EDITOR:: -onOpenProjectFromMenuBar::  Start Opening project from Menu Bar",)

        directory_name = QtWidgets.QFileDialog.getExistingDirectoryUrl(self, "Open graph from file")
        if directory_name != '':
            directory_path = directory_name.toString().split("file:///")[1]
            if os.path.isdir(directory_path):
                if self.validateProjectDirectory(directory_path):
                    if self.projectNeedsSaving():
                        self.project_path = directory_path
                        self.onOpenProject()
            else:
                QtWidgets.QMessageBox.warning(self, "Choosen path: ", self.project_path, " is not a valid Directory")
        else:
            QtWidgets.QMessageBox.warning(self, "Choosen path: ", self.project_path, " cannot be Empty!")

    def onOpenProject(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onOpenProject:: Opening Project from Path:: ", self.project_path)

        if self.display_overlay:
            self.setCentralWidget(self.tabs)
        self.display_overlay = False

        if CLASS_DEBUG: 
            print("MNRB_EDITOR:: dipslay Overlay:: ", self.display_overlay)
            print("MNRB_EDITOR:: QMain Windows in first tab widget::", self.getMainWindowWidgetsFromTab(0)[0])

        self.getNodeEditorTab().onOpenFile(self.mnrb_base_editor_path)
        self.getSkinningEditorTab().onOpenFile(self.mnrb_skinning_editor_path)
        self.statusBar().showMessage('Opened project from ' + str(self.project_path), 5000)

    def onSaveProject(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onSaveProject:: Start Saving Project")
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onSaveProject:: Saving To: ", self.project_path)

        if self.project_path is not None:

            self.getNodeEditorTab().onSaveFile(os.path.join(self.mnrb_base_editor_path, self.project_name + "_graph.json"))
            self.getSkinningEditorTab().onSaveFile(os.path.join(self.mnrb_skinning_editor_path, self.project_name + "_graph.json"))

            self.statusBar().showMessage(' Saved Project to ' + self.project_path, 5000)
            self.setTitleText()
            return True
        else:
            return self.onSaveProjectAs()

    def onSaveProjectAs(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --onSaveAsProject:: Start Saving As Project")

        directory_name = QtWidgets.QFileDialog.getExistingDirectoryUrl(self, "Save Project To Location")
        if directory_name != '':
            directory_path = directory_name.toString().split("file:///")[1]
            if os.path.isdir(directory_path):
                self.project_path = directory_path

                #create new Project Directory at ___Path
                
                #save all feature tabs to there new location
                self.getNodeEditorTab().onSaveFile(os.path.join(self.mnrb_base_editor_path, self.project_name + "_graph"))

                self.statusBar().showMessage(' Saved Project As to ' + self.project_path, 5000)
                self.setTitleText()

                return True
            else: 
                return False
        else: 
            return False

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

    def onNodeEditorAlignX(self):
        self.getNodeEditorTab().onAlignNodesX()

    def onNodeEditorAlignY(self):
        self.getNodeEditorTab().onAlignNodesY()

    def onNodeEditorMirrorNode(self):
        self.getNodeEditorTab().onMirrorNode()

    def onSceneMousePositionChange(self, x, y):
        self.statusMousePosition.setText("Scene Mouse Position: [%d %d]" % (x, y))

    def onPathItemPressed(self, item):
        self.overlayOpenActionButton.setEnabled(True)

    def onPathItemDoubleClicked(self, item):
        path_items = item.text().split(" - ")
        self.project_path = path_items[1]
        self.onOpenProject()

    def onOverlayOpenProject(self):
        current_path_items = self.current_workspace_projects_list.currentItem().text().split(" - ")
        self.project_path = current_path_items[1]
        self.onOpenProject()

    def onAbout(self):
        about_menu_messageBox = QtWidgets.QMessageBox()
        about_menu_messageBox.setWindowTitle("MNRB Information")
        about_menu_messageBox.setText("<PlaceHolder for description and documentation Link \n plus personal website link>")

        about_menu_messageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)

        about_menu_messageBox.exec()

    def onPropertiesDockWidget(self):
        if self.getNodeEditorTab().right_dock.isVisible():
            self.getNodeEditorTab().right_dock.hide()
        else:
            self.getNodeEditorTab().right_dock.show()
    
    def onNodeListDockWidget(self):
        if self.getNodeEditorTab().left_dock.isVisible():
            self.getNodeEditorTab().left_dock.hide()
        else:
            self.getNodeEditorTab().left_dock.show()

    def onOpenPreferences(self):
        self.preference_widget = MNRBPreferences()
        self.preference_widget.show()

    def isModified(self):
        return self.getNodeEditorTab().isModified()

    def closeEvent(self, event):
        if self.projectNeedsSaving():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    def projectNeedsSaving(self):
        if not self.isModified():
            return True
        else:
            result = QtWidgets.QMessageBox.warning(self, "Scene is not Saved!", "Document was modified. \n Do you want to Save Changed?", 
                                                   QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
            if result == QtWidgets.QMessageBox.Save:
                return self.onSaveProject()
            elif result == QtWidgets.QMessageBox.Cancel:
                return False
            else: return True
                 
    def loadProjectSettings(self):
        with open(self.project_settings_path, "r") as file:
            project_settings_raw = file.read()
            project_settings_json = json.loads(project_settings_raw)
        return project_settings_json

    def toggleActionCheckbox(self, action):
        is_checked = action.isChecked()
        action.setChecked(not is_checked)

    def updateNodeEditorMenu(self):
        if self.display_overlay or self.tabs.currentIndex() != 0:
            self.setNodeEditorMenuActions(False)
            self.action_align_on_x.setEnabled(False)
            self.action_align_on_y.setEnabled(False)
        else:
            self.setNodeEditorMenuActions(True)
            self.action_align_on_x.setEnabled(self.getNodeEditorTab().hasSelectedItems())
            self.action_align_on_y.setEnabled(self.getNodeEditorTab().hasSelectedItems())

        self.action_nodes_list_dock_visibility.setChecked(self.getNodeEditorTab().left_dock.isVisible())
        self.action_nodes_properties_dock_visibility.setChecked(self.getNodeEditorTab().right_dock.isVisible())

    def updateEditMenu(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --updateEditMenu:: Updating the edit menu functions!")

        if not self.display_overlay:
                current_tab = self.getCurrentTabWidget()

                try:
                    self.action_edit_paste.setEnabled(True)
                except Exception as e:
                    print(e)

                self.action_edit_cut.setEnabled(current_tab.canCut())
                self.action_edit_copy.setEnabled(current_tab.canCopy())
                self.action_delete.setEnabled(current_tab.canDelete())
                self.action_undo.setEnabled(current_tab.canUndo())
                self.action_redo.setEnabled(current_tab.canRedo())
                self.action_mirror_Node.setEnabled(current_tab.canMirrorNode())
        else:
            self.setEditMenuActions(False)

    def updateProjectMenu(self):
        if not self.display_overlay:
            self.setProjectMenuActions(True)
        else:
            self.setProjectMenuActions(False)
    
    def updateCurrentTab(self):
        self.getCurrentTabWidget().activate()

    def getNodeEditorTab(self):
        return self.tabs.widget(0).findChildren(QtWidgets.QMainWindow)[0]

    def getSkinningEditorTab(self):
        return self.tabs.widget(1).findChildren(QtWidgets.QWidget)[0]

    def getMainWindowWidgetsFromTab(self, tab_index):
        return self.tabs.widget(tab_index).findChildren(QtWidgets.QMainWindow)

    def getNodeEditorWidget(self):
        return self.tabs.widget(0).findChildren(QtWidgets.QMainWindow)[0].centralWidget()

    def getCurrentTabWidget(self):
        widgets_in_tab_widget = self.tabs.currentWidget().children()
        #if CLASS_DEBUG: print("MNRB_EDITOR:: --getCurrentTabWidget:: Widgets in Tab Widget:: ", widgets_in_tab_widget)
        tab_widget = None
        for widget in widgets_in_tab_widget:
            if hasattr(widget, "is_tab_widget"):
                tab_widget = widget
        return tab_widget

    def setNodeEditorMenuActions(self, state):
        self.action_load_template.setEnabled(state)
        self.actionSaveTemplateAs.setEnabled(state)
        self.action_clear.setEnabled(state)
        self.action_nodes_properties_dock_visibility.setEnabled(state)
        self.action_nodes_list_dock_visibility.setEnabled(state)

    def setEditMenuActions(self, state):
        self.action_edit_copy.setEnabled(state)
        self.action_edit_cut.setEnabled(state)
        self.action_edit_paste.setEnabled(state)
        self.action_delete.setEnabled(state)
        self.action_undo.setEnabled(state)
        self.action_redo.setEnabled(state)

    def setProjectMenuActions(self, state):
        self.action_save_project.setEnabled(state)

    def setTitleText(self):
        if CLASS_DEBUG: print("MNRB_EDITOR:: --setTitleText ")

        title = "MNRB Editor - "

        if self.project_name is not None:
            title += self.project_name
        else:
            self.setWindowTitle("MNRB Editor - Undefined")

        if not self.display_overlay:
            if self.isModified():
                title += "*"

        self.setWindowTitle(title)

    def set_statusBar_color(self, color, duration):
        original_stylesheet = self.statusBar().styleSheet()

        self.statusBar().setStyleSheet(f"background-color: {color}")

        QTimer.singleShot(duration, lambda: self.statusBar().setStyleSheet(original_stylesheet))

    def readSettings(self):
        if CLASS_DEBUG: print("MNRB_EDITOR: Reading Settings...")
        settings = QSettings("tlpf", "MNRB")
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        if CLASS_DEBUG: print("MNRB_EDITOR: Writing Settings...")
        settings = QSettings("tlpf", "MNRB")
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    def validateProjectDirectory(self, path):
        project_path_content = os.listdir(path)
        feature_tab_directories = [self.mnrb_base_editor_path_name, self.mnrb_skinning_editor_path_name]

        if CLASS_DEBUG:
            print("MNRB_EDITOR:: -validateProjectDirectory:: Project Path", self.project_path)
            print("MNRB_EDITOR:: -validateProjectDirectory:: Project Path Content", project_path_content)
            print("MNRB_EDITOR:: -validateProjectDirectory:: feature_tab_directories: ", feature_tab_directories)


        for feature_tab_directory in feature_tab_directories:
            if feature_tab_directory not in project_path_content:
                QtWidgets.QMessageBox.warning(self, "Could not Validate the project Structure of the choosen path: ", self.project_path)
                return False
            
        return True
    
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
    
    def __str__(self): return "ClassInstance::%s::  %s..%s" % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])