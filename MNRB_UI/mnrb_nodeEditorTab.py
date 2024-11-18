import os
import json
from PySide2 import QtWidgets, QtCore # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Widget import NodeEditorWidget # type: ignore

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

        # Left dock widget
        left_dock = QtWidgets.QDockWidget("Left Dock", self)
        left_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        left_dock_contents = QtWidgets.QWidget()
        left_dock_layout = QtWidgets.QVBoxLayout(left_dock_contents)
        left_dock_label = QtWidgets.QLabel("This is the left dock widget.")
        left_dock_layout.addWidget(left_dock_label)
        left_dock_contents.setLayout(left_dock_layout)
        left_dock.setWidget(left_dock_contents)

        # Add the left dock widget to the secondary main window
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, left_dock)

        # Right dock widget
        right_dock = QtWidgets.QDockWidget("Right Dock", self)
        right_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        right_dock_contents = QtWidgets.QWidget()
        right_dock_layout = QtWidgets.QVBoxLayout(right_dock_contents)
        right_dock_label = QtWidgets.QLabel("This is the right dock widget.")
        right_dock_layout.addWidget(right_dock_label)
        right_dock_contents.setLayout(right_dock_layout)
        right_dock.setWidget(right_dock_contents)
        
        # Add the right dock widget to the secondary main window
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, right_dock)

    def onOpenFile(self, path):
        if os.path.isdir(path):
            graph = os.listdir(path)[0]

            if len(graph) >= 1:
                self.central_widget.scene.loadSceneFromFile(os.path.join(path, graph))
                #add History Stamp
        elif os.path.isfile(path):
            self.central_widget.scene.loadSceneFromFile(path)
            #add History Stamp
    
    def clearScene(self):
        self.central_widget.scene.clearScene()

    def onSaveFile(self, file_name):
        self.central_widget.scene.saveSceneToFile(file_name)

    def onNewFile(self, path):
        pass

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

        self.central_widget.scene.clipboard.deserializeFromClipboardToScene()