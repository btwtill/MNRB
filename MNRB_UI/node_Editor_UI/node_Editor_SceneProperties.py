import os
from enum import Enum
from PySide2 import QtWidgets #type: ignore 
from PySide2.QtCore import Qt, QSize #type: ignore
from PySide2.QtGui import QPixmap, QIcon #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_PropertiesWidget import NodeEditorPropertiesWidget #type: ignore

EVENT_DEBUG = False
VALIDATION_DEBUG = False
SERIALIZATION_DEBUG = False

class ScenePropertyStateIcon(Enum):
    valid = os.path.join(os.path.dirname(__file__), "..", "icons", "valid.png")
    invalid = os.path.join(os.path.dirname(__file__), "..", "icons", "invalid.png")

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
        self.rig_name_line_edit.editingFinished.connect(self.setHasBeenModified)
        self.layout.addWidget(self.rig_name_line_edit)

        self.connectHasBeenModifiedCallback(self.updateRigName)
        self.connectHasBeenModifiedCallback(self.setSceneModified)

    def initActions(self):
        self.action_layout = QtWidgets.QVBoxLayout()

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
            self.setInvalid("Invalid Component Name!!")
            return False
        
        if not self.validateNodes():
            self.setInvalid("No components are valid!!")
            return False
        
        if not self.validateDuplicateNaming():
            self.setInvalid("Duplicate Names detected!!")
            return False

        self.setValid()
        return True

    def validRigName(self):
        if self.rig_name_line_edit.text() != "" and self.rig_name_line_edit.text() != "Undefined" :
            return True
        else:
            return False

    def validateNodes(self):
        if VALIDATION_DEBUG: print("SCENE_PROPERTIES:: --validateNodes: Nodes to be checked:: ", self.scene.nodes)
        is_one_node_valid = False
        for node in self.scene.nodes:
            if VALIDATION_DEBUG: print("SCENE_PROPERTIES:: --validateNodes:: ", node.properties.is_valid)
            if node.properties.is_valid:
                is_one_node_valid = True

        if not is_one_node_valid:
            
            return False
        return True if is_one_node_valid else False

    def validateDuplicateNaming(self):
        is_duplicate_component_name = False
        encounters = set()
        for node in self.scene.nodes:
            component_name = node.properties.component_name
            if component_name in encounters or component_name == self.rig_name:
                is_duplicate_component_name = True
                break
            encounters.add(component_name)

        return False if is_duplicate_component_name else True

    def setInvalid(self, message):
        self.is_valid = False
        self.status_bar.showMessage("Scene Status Invalid:: " + message)
        self.setStatusBarIconLabel(ScenePropertyStateIcon.invalid)

    def setValid(self):
        self.is_valid = True
        self.status_bar.showMessage("Scene Status Valid:: Ready to Build!!")
        self.setStatusBarIconLabel(ScenePropertyStateIcon.valid)

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

        if SERIALIZATION_DEBUG: print("SCENE_PROPERTIES:: --deserialize:: current rig_name:: ", self.rig_name)
        self.rig_name_line_edit.setText(data['rig_name'])
        if SERIALIZATION_DEBUG: print("SCENE_PROPERTIES:: --deserialize::  setting Line Edit Text to::", data['rig_name'])
        self.setHasBeenModified()
        self.is_silent = False

        if SERIALIZATION_DEBUG: print("SCENE_PROPERTIES:: --deserialize:: current rig_name:: ", self.rig_name)
        self.validateProperties()
        
        if SERIALIZATION_DEBUG: print("SCENE_PROPERTIES:: ___________END SCENE PROPERTIES DESERIALIZATION")
        return True