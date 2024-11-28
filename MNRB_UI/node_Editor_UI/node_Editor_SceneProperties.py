import os
from enum import Enum
from PySide2 import QtWidgets #type: ignore 
from PySide2.QtCore import Qt, QSize #type: ignore
from PySide2.QtGui import QPixmap, QIcon #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_PropertiesWidget import NodeEditorPropertiesWidget #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

EVENT_DEBUG = False
VALIDATION_DEBUG = True

class ScenePropertyStateIcon(Enum):
    valid = os.path.join(os.path.dirname(__file__), "..", "icons", "default.png")
    invalid = os.path.join(os.path.dirname(__file__), "..", "icons", "base_component.png")

class NodeEditorSceneProperties(NodeEditorPropertiesWidget):
    def __init__(self, scene, parent=None) -> None:
        super().__init__(parent)

        self.scene = scene

        self.is_silent = True

        self.title = "Scene Properties"
        self.rig_name = "Undefined"
        
        self.updateActionButtons()

    def initUI(self):
        #Rig Name
        rig_name_label = QtWidgets.QLabel("Define the overall name for your Rig!")
        rig_name_label.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(rig_name_label)

        self.rig_name_line_edit = QtWidgets.QLineEdit()
        self.rig_name_line_edit.setPlaceholderText("No Name Defined:")
        self.rig_name_line_edit.setAlignment(Qt.AlignCenter)
        self.rig_name_line_edit.textChanged.connect(self.setHasBeenModified)
        self.layout.addWidget(self.rig_name_line_edit)

        self.connectHasBeenModifiedCallback(self.updateRigName)
        self.connectHasBeenModifiedCallback(self.setSceneModified)

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

        status_bar_layout = QtWidgets.QHBoxLayout()

        self.status_bar_icon_label = QtWidgets.QLabel()
        self.setStatusBarIconLabel(ScenePropertyStateIcon.valid)
        
        status_bar_layout.addWidget(self.status_bar_icon_label)

        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.showMessage("Scene Messages:: Ready")

        status_bar_layout.addWidget(self.status_bar)

        self.layout.addLayout(status_bar_layout)
        self.setLayout(self.layout)

        self.connectHasBeenModifiedCallback(self.validateProperties)
        self.connectIsValidCallback(self.updateActionButtons)

    def validateProperties(self):
        if VALIDATION_DEBUG: print("SCENE_PROPERTIES:: --validateProperties: Start Validation")
        if not self.validRigName():
            self.is_valid = False
            self.status_bar.showMessage("Scene Status:: Invalid Component Name!!")
            self.setStatusBarIconLabel(ScenePropertyStateIcon.invalid)
            return False
        
        if VALIDATION_DEBUG: print("SCENE_PROPERTIES:: --validateProperties: Nodes to be checked:: ", self.scene.nodes)
        
        is_one_node_valid = False
        for node in self.scene.nodes:
            if VALIDATION_DEBUG: print("SCENE_PROPERTIES:: --validateProperties:: ", node.properties.is_valid)
            if node.properties.is_valid:
                is_one_node_valid = True
        if not is_one_node_valid:
            self.is_valid = False
            self.status_bar.showMessage("Scene Status:: No Component is Valid!!")
            self.setStatusBarIconLabel(ScenePropertyStateIcon.invalid)
            return False
        
        is_duplicate_component_name = False
        encounters = set()
        for node in self.scene.nodes:
            component_name = node.properties.component_name
            if component_name in encounters:
                is_duplicate_component_name = True
                break
            encounters.add(component_name)

        if is_duplicate_component_name:
            self.is_valid =False
            self.status_bar.showMessage("Scene Status:: Duplicate component names Found!!")
            self.setStatusBarIconLabel(ScenePropertyStateIcon.invalid)
            return False

        self.is_valid = True
        self.status_bar.showMessage("Scene Status:: Ready")
        self.setStatusBarIconLabel(ScenePropertyStateIcon.valid)
        return True

    def validRigName(self):
        if self.rig_name_line_edit.text() != "":
            return True
        else:
            return False

    def updateActionButtons(self):
        self.build_guides_action_button.setEnabled(self.is_valid)
        self.build_static_action_button.setEnabled(self.is_valid)
        self.build_component_action_button.setEnabled(self.is_valid)
        self.connect_component_action_button.setEnabled(self.is_valid)

    def updateRigName(self):
        self.rig_name = self.rig_name_line_edit.text()

    def getRigName(self):
        return self.rig_name

    def setSceneModified(self):
        if not self.is_silent:
            self.scene.setModified(True)

    def setStatusBarIconLabel(self, icon_path):
        pixmap = QPixmap(icon_path.value)
        self.status_bar_icon_label.setPixmap(pixmap)

    def onBuildGuides(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onBuildGuides:: Building Guides!")
        self.scene.buildSceneGuides()

    def onBuildStatic(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onBuildStatic:: Building Static")
        self.scene.buildSceneStatic()

    def onBuildComponent(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onBuildComponent:: Building Component ")
        self.scene.buildSceneComponents()

    def onConnectComponents(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onConnectComponents:: Connecting Components")
        self.scene.connectSceneComponents()

    def serialize(self):
        result_data = super().serialize()
        result_data['rig_name'] = self.rig_name
        return result_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True):
        result = super().deserialize(data, hashmap, restore_id)

        self.rig_name_line_edit.setText(data['rig_name'])

        self.is_silent = False
        return True