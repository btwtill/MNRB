import os
import json
from PySide2 import QtWidgets, QtCore # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Widget import NodeEditorWidget # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_DragNodeList import NodeEditorDragNodeList #type: ignore

class mnrb_NodeEditorTab(QtWidgets.QMainWindow):
    def __init__(self, ):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Central widget for secondary main window
        self.central_widget = NodeEditorWidget()

        # Set the central widget for the secondary main window
        self.setCentralWidget(self.central_widget)

        # Add dock widgets to the secondary main window
        self.add_dock_widgets()

    def add_dock_widgets(self):
        """Add left and right dock widgets to the secondary main window."""

        self.node_list_widget = NodeEditorDragNodeList()

        # Left dock widget
        self.left_dock = QtWidgets.QDockWidget("Node List", self)
        self.left_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.left_dock.setWidget(self.node_list_widget)

        # Add the left dock widget to the secondary main window
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.left_dock)

        # Right dock widget
        self.right_dock = QtWidgets.QDockWidget("Node Properties", self)
        self.right_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        right_dock_contents = QtWidgets.QWidget()
        right_dock_layout = QtWidgets.QVBoxLayout(right_dock_contents)
        right_dock_label = QtWidgets.QLabel("This is the right dock widget.")
        right_dock_layout.addWidget(right_dock_label)
        right_dock_contents.setLayout(right_dock_layout)
        self.right_dock.setWidget(right_dock_contents)
        
        # Add the right dock widget to the secondary main window
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.right_dock)

    def onOpenFile(self, path):
        if os.path.isdir(path):
            graph_items = os.listdir(path)

            if len(graph_items) >= 1:
                self.central_widget.scene.loadSceneFromFile(os.path.join(path, graph_items[0]))
                #add History Stamp
            else:
                self.onNewFile()
                
        elif os.path.isfile(path):
            self.central_widget.scene.loadSceneFromFile(path)
            #add History Stamp
    
    def clearScene(self):
        self.central_widget.scene.clearScene()

    def onSaveFile(self, file_name):
        self.central_widget.scene.saveSceneToFile(file_name)

    def onNewFile(self):
        self.central_widget.scene.clearScene()

    def onDelete(self):
        self.central_widget.view.deleteSelected()
    
    def onUndo(self):
        self.central_widget.scene.history.undo()

    def onRedo(self):
        self.central_widget.scene.history.redo()

    def onEditCopy(self):
        data = self.central_widget.scene.clipboard.serializeSceneToClipboard()
        str_data = json.dumps(data, indent=4)
        QtWidgets.QApplication.instance().clipboard().setText(str_data)

    def onEditCut(self):
        data = self.central_widget.scene.clipboard.serializeSceneToClipboard(delete = True)
        str_data = json.dumps(data, indent=4)
        QtWidgets.QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        raw_data = QtWidgets.QApplication.instance().clipboard().text()

        try:    
            data = json.loads(raw_data)
        except ValueError as e:
            print("Pasting of invalid Json Data!", e)
            return
            
        if 'nodes' not in data: 
            print("Json does not contain any nodes!!")
            return

        self.central_widget.scene.clipboard.deserializeFromClipboardToScene(data)
    
    def isModified(self):
        return self.central_widget.scene.has_been_modified