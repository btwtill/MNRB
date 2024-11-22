from PySide2 import QtWidgets #type: ignore
from PySide2.QtCore import QSize  #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore

EVENT_DEBUG = True

class NodeEditorProperties(QtWidgets.QWidget, Serializable):
    def __init__(self, node = None, parent=None) -> None:
        super().__init__(parent)

        self.node = node
        self._title = "undefined"

        self.initUI()
        self.initActions()

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        if self.node is not None:
            self._title = self.node.title + " Properties"
        else:
            self._title = value

    def initUI(self):
        #Title Label
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addStretch()

    def initActions(self):

        self.action_layout = QtWidgets.QHBoxLayout()
        self.build_guides_action_button = QtWidgets.QPushButton("Build Guides")
        self.build_guides_action_button.clicked.connect(self.onBuildGuides)

        self.build_static_action_button = QtWidgets.QPushButton("Build Static")
        self.build_static_action_button.clicked.connect(self.onBuildStatic)

        self.build_component_action_button = QtWidgets.QPushButton("Build")
        self.build_component_action_button.clicked.connect(self.onBuildComponent)

        self.connect_component_action_button = QtWidgets.QPushButton("Connect")
        self.connect_component_action_button.clicked.connect(self.onConnectComponents)

        self.action_layout.addWidget(self.build_guides_action_button)
        self.action_layout.addWidget(self.build_static_action_button)
        self.action_layout.addWidget(self.build_component_action_button)
        self.action_layout.addWidget(self.connect_component_action_button)

        self.layout.addLayout(self.action_layout)

        self.setLayout(self.layout)

    def onBuildGuides(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onBuildGuides:: Building Guides!")

    def onBuildStatic(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onBuildStatic:: Building Static")

    def onBuildComponent(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onBuildComponent:: Building Component ")

    def onConnectComponents(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onConnectComponents:: Connecting Components")

    def setTitle(self, value):
        self.title = value

    def serialize(self):
        return True
    
    def deserialize(self, data, hashmap = {}, restore_id=True):
        return False