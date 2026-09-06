import os
import json
from PySide6 import QtWidgets #type: ignore
from PySide6.QtCore import Qt, QTimer #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_Widget import PipelineEditorWidget #type: ignore
from MNRB.ROSE_UI.UI_GraphicComponents.scrollable_dock_widget import ScrollableDockWidget #type: ignore

CLASS_DEBUG = False

class rose_PipelineEditorTab(QtWidgets.QMainWindow):
    """Mirrors rose_nodeEditorTab.py's shape for the pipeline canvas - no left-dock
    drag list (steps are added via the canvas's right-click "add step" menu
    instead, see PipelineEditorWidget.handleNewStepContextMenu)."""

    def __init__(self, node_editor_tab, skinning_tab):
        super().__init__()
        self.is_tab_widget = True

        self.node_editor_tab = node_editor_tab
        self.skinning_tab = skinning_tab

        self.initUI()

    def initUI(self):
        self.add_dock_widgets()

        self.central_widget = PipelineEditorWidget(self.right_dock, self.node_editor_tab, self.skinning_tab)
        self.setCentralWidget(self.central_widget)

        #deferred to the next event loop tick so the view already has its real
        #layout size by the time it centers, same reasoning as the node editor tab
        QTimer.singleShot(0, self.centerPipelineView)

    def add_dock_widgets(self):
        self.right_dock_title = "Pipeline Properties"
        #same reasoning as the node editor's properties dock - the Output Path
        #step's panel already outgrows it
        self.right_dock = ScrollableDockWidget(self.right_dock_title, self)
        self.right_dock.title = self.right_dock_title
        self.right_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.right_dock.setMinimumWidth(250)

        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

    def clearScene(self):
        self.central_widget.scene.clearScene()

    def centerPipelineView(self):
        self.central_widget.centerView()

    def hasSelectedItems(self):
        return self.central_widget.sceneHasSelectedItems()

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

    def canMirrorNode(self):
        #mirroring (L/R prefix + guide position flip) is a rig-authoring concept,
        #doesn't apply to pipeline steps
        return False

    def loadFile(self, path):
        try:
            self.central_widget.scene.loadSceneFromFile(path)
        except Exception as e:
            #a corrupted/truncated/empty graph file (e.g. left behind by a save
            #that failed partway through) shouldn't take down the whole project
            #open flow - fall back to a blank pipeline instead
            print("rose_PipelineEditorTab:: --loadFile:: Failed to load '%s': %s - starting a blank pipeline instead" % (path, e))
            self.onNewFile()

        self.central_widget.scene.history.clear()
        self.central_widget.scene.history.storeHistory("Inital History Stamp")

    def onOpenFile(self, path):
        if os.path.isdir(path):
            graph_items = os.listdir(path)
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
        try:
            self.central_widget.scene.history.undo()
        except Exception as e: print(e)

    def onRedo(self):
        try:
            self.central_widget.scene.history.redo()
        except Exception as e: print(e)

    def onEditCopy(self):
        data = self.central_widget.scene.clipboard.serializeSceneToClipboard()
        QtWidgets.QApplication.instance().clipboard().setText(json.dumps(data, indent=4))

    def onEditCut(self):
        data = self.central_widget.scene.clipboard.serializeSceneToClipboard(delete = True)
        QtWidgets.QApplication.instance().clipboard().setText(json.dumps(data, indent=4))

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

    def onAlignNodesX(self):
        self.central_widget.scene.alignSelectedNodesOnX()

    def onAlignNodesY(self):
        self.central_widget.scene.alignSelectedNodesOnY()

    def isModified(self):
        return self.central_widget.scene.isModified()

    def activate(self):
        pass

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])
