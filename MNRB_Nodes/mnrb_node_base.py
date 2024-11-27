from PySide2.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton #type: ignore
from PySide2.QtCore import Qt #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_NodeProperties import NodeEditorNodeProperties #type: ignore
from MNRB.global_variables import GUIDE_HIERARCHY_SUFFIX #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

CLASS_DEBUG = True

class MNRB_NodeProperties(NodeEditorNodeProperties):
    def __init__(self, node):
        super().__init__(node)

        self.component_name = "Undefined"
        self.is_silent = True

        self.updateActionButtons(self.is_valid)

    def initUI(self):
        #component Name Label
        component_name_label = QLabel("Set Component Name:")
        component_name_label.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(component_name_label)

        #component Name
        self.component_name_edit = QLineEdit()
        self.component_name_edit.setPlaceholderText("Enter Component Name: ")
        self.component_name_edit.setAlignment(Qt.AlignCenter)
        self.component_name_edit.textChanged.connect(self.setHasBeenModified)
        self.layout.addWidget(self.component_name_edit)
        self.layout.addStretch()

        self.connectHasBeenModifiedCallback(self.updateComponentName)
        self.connectHasBeenModifiedCallback(self.setSceneModified)

    def initActions(self):
        self.action_layout = QHBoxLayout()

        self.build_guides_action_button = QPushButton("Build Guides")
        self.build_guides_action_button.clicked.connect(self.onBuildGuides)

        self.build_static_action_button = QPushButton("Build Static")
        self.build_static_action_button.clicked.connect(self.onBuildStatic)

        self.build_component_action_button = QPushButton("Build")
        self.build_component_action_button.clicked.connect(self.onBuildComponent)

        self.connect_component_action_button = QPushButton("Connect")
        self.connect_component_action_button.clicked.connect(self.onConnectComponents)

        self.action_layout.addWidget(self.build_guides_action_button)
        self.action_layout.addWidget(self.build_static_action_button)
        self.action_layout.addWidget(self.build_component_action_button)
        self.action_layout.addWidget(self.connect_component_action_button)

        self.layout.addLayout(self.action_layout)
        self.setLayout(self.layout)

        self.connectHasBeenModifiedCallback(self.validateProperties)
        self.connectIsValidCallback(self.updateActionButtons)

    def validateProperties(self):
        if not self.validComponentName():
            self.is_valid = False
            return False
        self.is_valid = True
        return True

    def validComponentName(self):
        if self.component_name_edit.text() != "" and self.component_name_edit.text() != "Undefined":
            return True
        else:
            return False

    def updateActionButtons(self, state):
        self.build_guides_action_button.setEnabled(state)
        self.build_static_action_button.setEnabled(state)
        self.build_component_action_button.setEnabled(state)
        self.connect_component_action_button.setEnabled(state)

    def updateComponentName(self):
        self.component_name = self.component_name_edit.text()

    def setSceneModified(self):
        if not self.is_silent:
            self.node.scene.setModified(True)

    def onBuildGuides(self):
        if CLASS_DEBUG: print("BaseNodeProperties:_ --onBuildGuides ", self.node)
        self.node.guideBuild()

    def onBuildStatic(self):
        if CLASS_DEBUG: print("BaseNodeProperties:_ --onBuildStatic ", self.node)
        self.node.staticBuild()

    def onBuildComponent(self):
        if CLASS_DEBUG:  print("BaseNodeProperties:: --onBuildComponent: ", self.node)
        self.node.componentBuild()

    def onConnectComponents(self):
        if CLASS_DEBUG: print("BaseNodeProperties:: --onConnectComponent: ", self.node)
        self.node.connectComponent()

    def serialize(self):
        result_data = super().serialize()
        result_data['component_name'] = self.component_name
        return result_data
    
    def deserialize(self, data, hashmap = {}, restore_id=True):
        result = super().deserialize(data, hashmap, restore_id)
        self.component_name_edit.setText(data['component_name'])
        self.is_silent = False

        return True

class MNRB_Node(NodeEditorNode):
    operation_code = 0
    operation_title = "MNRB_Node"
    icon = None

    Node_Properties_Class = MNRB_NodeProperties

    def __init__(self, scene, inputs=[], outputs=[]):
        super().__init__(scene, self.__class__.operation_title, inputs, outputs)

        self.component_hierarchy = None
        self.guides = []

        self.controls = []
        self.deforms = []

        self.properties.connectHasBeenModifiedCallback(self.updateComponentHierarchyName)

    def guideBuild(self) -> str:
        if not self.scene.scene_rig_hierarchy.isGuideHierarchy():
            self.scene.scene_rig_hierarchy.createGuideHierarchy()
            current_guide_hierarchy = self.scene.scene_rig_hierarchy.getGuideHierarchyName()
            if CLASS_DEBUG: print("%s:: --guideBuild:: " % self.__class__.__name__, current_guide_hierarchy)
        else:
            current_guide_hierarchy = self.scene.scene_rig_hierarchy.getGuideHierarchyName()

        if self.component_hierarchy is not None:
            if MC.objectExists(self.component_hierarchy):
                MC.deleteObjectWithHierarchy(self.component_hierarchy)

        current_component_guide_hierarchy_name = self.properties.component_name + GUIDE_HIERARCHY_SUFFIX
        current_component_guide_hierarchy = MC.createTransform(current_component_guide_hierarchy_name)
        if CLASS_DEBUG: print("%s:: --guideBuild:: Object to be parented: " % self.__class__.__name__, "Child:: ",current_component_guide_hierarchy, " Parent:: ", current_guide_hierarchy)
        MC.parentObject(current_component_guide_hierarchy, current_guide_hierarchy)
        self.component_hierarchy = current_component_guide_hierarchy
            
        return current_guide_hierarchy

    def staticBuild(self):
        raise NotImplementedError
    
    def componentBuild(self):
        raise NotImplementedError
    
    def connectComponent(self):
        raise NotImplementedError

    def updateComponentHierarchyName(self):
        if self.component_hierarchy is not None:
            try:
                new_component_hierarchy_name = self.properties.component_name + GUIDE_HIERARCHY_SUFFIX
                new_name = MC.renameObject(self.component_hierarchy, new_component_hierarchy_name)
                if new_name != self.component_hierarchy:
                    self.component_hierarchy = new_name
            except Exception as e:
                if CLASS_DEBUG: print("%s:: --updateComponentHierarchyName:: ERROR:: ", e)

    def serialize(self):
        result_data = super().serialize()
        result_data['operation_code'] = self.__class__.operation_code
        result_data['component_hierarchy'] = self.component_hierarchy
        return result_data
    
    def deserialize(self, data, hashmap={}, restore_id = True, exists=False):
        result = super().deserialize(data, hashmap, restore_id, exists)
        self.component_hierarchy = data['component_hierarchy']
        return True