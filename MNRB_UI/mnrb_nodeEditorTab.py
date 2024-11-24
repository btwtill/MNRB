import os
import json
from PySide2 import QtWidgets # type: ignore
from PySide2.QtCore import QIODevice, QDataStream, Qt #type: ignore
from PySide2.QtGui  import QPixmap #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Widget import NodeEditorWidget # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_DragNodeList import NodeEditorDragNodeList #type: ignore
from MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_FileException import InvalidFile #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import NODELIST_MIMETYPE #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node #type: ignore

DRAGDROP_DEBUG = True

class mnrb_NodeEditorTab(QtWidgets.QMainWindow):
    def __init__(self, ):
        super().__init__()
        self.is_tab_widget = True

        self.initUI()

    def initUI(self):
    
        # Add dock widgets to the secondary main window
        self.add_dock_widgets()

        # Central widget for secondary main window
        self.central_widget = NodeEditorWidget(self.right_dock)

        # Set the central widget for the secondary main window
        self.setCentralWidget(self.central_widget)

        self.central_widget.scene.connectViewDragEnterListenerCallback(self.onDragEnter)
        self.central_widget.scene.connectViewDropListenerCallback(self.onDrop)

    def add_dock_widgets(self):
        """Add left and right dock widgets to the secondary main window."""

        self.node_list_widget = NodeEditorDragNodeList()

        # Left dock widget
        self.left_dock = QtWidgets.QDockWidget("Node List", self)
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.left_dock.setWidget(self.node_list_widget)

        # Add the left dock widget to the secondary main window
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        # Right dock widget
        self.right_dock_title = "Node Properties"
        self.right_dock = QtWidgets.QDockWidget(self.right_dock_title, self)
        self.right_dock.title = self.right_dock_title

        self.right_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        right_dock_contents = QtWidgets.QWidget()
        right_dock_layout = QtWidgets.QVBoxLayout(right_dock_contents)
        right_dock_label = QtWidgets.QLabel("This is the right dock widget.")
        right_dock_layout.addWidget(right_dock_label)
        right_dock_contents.setLayout(right_dock_layout)
        self.right_dock.setWidget(right_dock_contents)
        self.right_dock.setMinimumWidth(250)

        # Add the right dock widget to the secondary main window
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

    def clearScene(self):
        self.central_widget.scene.clearScene()

    def canCut(self):
        return self.central_widget.sceneHasSelectedItems()

    def canCopy(self):
        return self.central_widget.sceneHasSelectedItems()

    def canUndo(self):
        return self.central_widget.scene.history.canUndo()

    def canRedo(self):
        return self.central_widget.scene.history.canRedo()

    def canDelete(self):
        return self.central_widget.sceneHasSelectedItems()

    def loadFile(self, path):
        try:
            self.central_widget.scene.loadSceneFromFile(path)
            #self.central_widget.scene.history.clear()
            #self.central_widget.scene.history.storeHistory("Inital History Stamp")
            #self.central_widget.centerView()
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.warning(self, "Error Occured during the loading of the File at: ", path)

    def onOpenFile(self, path):
        if os.path.isdir(path):
            graph_items = os.listdir(path)

            #check if there is a graph in the current project directory if not create a new one
            if len(graph_items) >= 1:
                self.loadFile(os.path.join(path, graph_items[0]))
            else:
                self.onNewFile()
                
        elif os.path.isfile(path):
            self.loadFile(path)


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
    
    def onDrop(self, event):
        if DRAGDROP_DEBUG: print("NODEEDITORTAB:: --onDrop:: Drop it like its hot!:: ", event)
        if event.mimeData().hasFormat(NODELIST_MIMETYPE):
            event_data = event.mimeData().data(NODELIST_MIMETYPE)
            data_stream = QDataStream(event_data, QIODevice.ReadOnly)
            pixmap = QPixmap()
            data_stream >> pixmap
            operation_code = data_stream.readInt32()
            text = data_stream.readQString()

            if DRAGDROP_DEBUG: print("NODEEDITORTAB:: --onDrop:: Got Data:: OperationCode:: ", operation_code, " and Name:: ", text)

            mouse_position = event.pos()
            scene_position = self.central_widget.scene.getView().mapToScene(mouse_position)
            
            if DRAGDROP_DEBUG: print("NODEEDITORTAB:: --onDrop:: Event ScenePosition:: ", scene_position)

            new_node = MNRB_Node(self.central_widget.scene, inputs = [["base_def", 1, True]], outputs = [["base_def", 1, True], ["base_ctrl", 2, True]])
            new_node.setPosition(scene_position.x(), scene_position.y())

            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            if DRAGDROP_DEBUG: print("NODEEDITORTAB:: --onDrop:: Not Requested Format:: ", NODELIST_MIMETYPE, " ignoring event")
            event.ignore()

    def onDragEnter(self, event):
        if DRAGDROP_DEBUG: print("NODEEDITORTAB:: --onDragEnter:: Passport please, you are entering view Area!:: ", event)
        if DRAGDROP_DEBUG: print("NODEEDITORTAB:: --onDragEnter:: mimedata:: ", event.mimeData().hasFormat(NODELIST_MIMETYPE))
        if event.mimeData().hasFormat(NODELIST_MIMETYPE):
            event.acceptProposedAction()
        else:
            print("NODEEDITORTAB:: --onDragEnter:: Drag Enter Denied!")

    def isModified(self):
        return self.central_widget.scene.isModified()