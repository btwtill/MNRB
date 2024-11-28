import math
from PySide2.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QCheckBox, QSlider #type: ignore
from PySide2.QtCore import Qt #type: ignore
from PySide2.QtGui import QDoubleValidator #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_NodeProperties import NodeEditorNodeProperties #type: ignore
from MNRB.global_variables import GUIDE_HIERARCHY_SUFFIX #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_colors.colors import MNRBColor #type: ignore

CLASS_DEBUG = True
VALIDATE_DEBUG = True

class MNRB_NodeProperties(NodeEditorNodeProperties):
    def __init__(self, node):
        super().__init__(node)

        self.component_name = "Undefined"
        self.is_disabled = False
        self.is_silent = True

        self.guide_size = 1.0
        self.deform_size = 1.0

        self.updateActionButtons()

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

        #add disable check
        self.disabled_checkbox = QCheckBox("Disable Component")
        self.disabled_checkbox.stateChanged.connect(self.setHasBeenModified)
        self.layout.addWidget(self.disabled_checkbox)
        
        #Guide Size Adjustment
        guide_slider_label_layout = QHBoxLayout()
        guide_size_slider_label = QLabel("Guide Size:")
        guide_size_slider_label.setAlignment(Qt.AlignCenter)
        guide_slider_label_layout.addWidget(guide_size_slider_label)

        self.guide_slider_size_edit = QLineEdit()
        self.guide_slider_size_edit.setText(str(1.0))
        self.guide_slider_size_edit.textChanged.connect(self.onGuideSizeEditChange)

        guide_slider_label_layout.addWidget(guide_size_slider_label)
        guide_slider_label_layout.addWidget(self.guide_slider_size_edit)

        self.layout.addLayout(guide_slider_label_layout)

        self.guide_size_slider = QSlider(Qt.Horizontal)
        self.guide_size_slider.setMinimum(0)
        self.guide_size_slider.setMaximum(10000)
        self.guide_size_slider.setValue(100)
        self.guide_size_slider.setTickPosition(QSlider.TicksBelow)
        self.guide_size_slider.setTickInterval(20)
        self.guide_size_slider.valueChanged.connect(self.onGuideSliderChange)

        self.layout.addWidget(self.guide_size_slider)

        #deform Size Adjustment
        deform_slider_label_layout = QHBoxLayout()
        deform_size_slider_label = QLabel("Deform Size:")
        deform_size_slider_label.setAlignment(Qt.AlignCenter)
        deform_slider_label_layout.addWidget(deform_size_slider_label)

        self.deform_slider_size_edit = QLineEdit()
        self.deform_slider_size_edit.setText(str(1.0))
        self.deform_slider_size_edit.textChanged.connect(self.onDeformSizeEditChange)

        deform_slider_label_layout.addWidget(deform_size_slider_label)
        deform_slider_label_layout.addWidget(self.deform_slider_size_edit)

        self.layout.addLayout(deform_slider_label_layout)

        self.deform_size_slider = QSlider(Qt.Horizontal)
        self.deform_size_slider.setMinimum(0)
        self.deform_size_slider.setMaximum(10000)
        self.deform_size_slider.setValue(100)
        self.deform_size_slider.setTickPosition(QSlider.TicksBelow)
        self.deform_size_slider.setTickInterval(20)
        self.deform_size_slider.valueChanged.connect(self.onDeformSliderChange)

        self.layout.addWidget(self.deform_size_slider)

        self.layout.addStretch()
        self.connectHasBeenModifiedCallback(self.updateDisabledState)
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
        if VALIDATE_DEBUG: print("%s:: --validateProperties:: Start Validating properties!" % self.__class__.__name__)

        if not self.validComponentName():
            self.is_valid = False
            return False
        
        if VALIDATE_DEBUG: print("%s:: --validateProperties:: Valid Component Name: " % self.__class__.__name__, self.component_name)

        if self.is_disabled:
            self.is_valid = False
            return False
        
        if VALIDATE_DEBUG: print("%s:: --validateProperties:: Component is Disabled:  "% self.__class__.__name__ , self.is_disabled)

        self.is_valid = True
        return True

    def validComponentName(self):
        if self.component_name_edit.text() != "" and self.component_name_edit.text() != "Undefined":
            return True
        else:
            return False

    def onGuideSizeEditChange(self):
        self.updateGuideSlider()
        self.updateGuideSize()

    def onGuideSliderChange(self):
        self.updateGuideSliderSizeEdit()
        self.updateGuideSize()

    def updateGuideSize(self):
        #update the guide size valule
        self.guide_size = float(self.guide_slider_size_edit.text())
        #call the nodes guide resize funcion
        if CLASS_DEBUG: print("%s:: --updateGuideSize:: Setting Guide Size To: " % self.__class__.__name__, self.guide_size)
        if CLASS_DEBUG: print("%s:: --updateGuideSize:: of Node::  " % self.__class__.__name__, self.node)
        self.node.setComponentGuideSize(self.guide_size)
        #set properties to be modified
        self.setHasBeenModified()

    def onDeformSizeEditChange(self):
        self.updateDeformSlider()
        self.updateDeformSize()

    def onDeformSliderChange(self):
        self.updateDeformSliderEdit()
        self.updateDeformSize()

    def updateDeformSize(self):
        self.deform_size = float(self.deform_slider_size_edit.text())
        if CLASS_DEBUG: print("%s:: --updateDeformSize:: Setting Deform Size To: " % self.__class__.__name__, self.deform_size)
        if CLASS_DEBUG: print("%s:: --updateDeformSize:: of Node::  " % self.__class__.__name__, self.node)
        self.node.setComponentDeformRadius(self.deform_size)
        self.setHasBeenModified()

    def updateDisabledState(self):
        self.is_disabled = self.disabled_checkbox.isChecked()

    def updateGuideSlider(self):
        self.guide_size_slider.setValue(self.formatSliderEditToSliderValue(self.guide_slider_size_edit.text()))

    def updateGuideSliderSizeEdit(self):
        self.guide_slider_size_edit.setText(str(self.formatSliderValueToEditValue(self.guide_size_slider.value())))

    def updateDeformSlider(self):
        self.deform_size_slider.setValue(self.formatSliderEditToSliderValue(self.deform_slider_size_edit.text()))

    def updateDeformSliderEdit(self):
        self.deform_slider_size_edit.setText(str(self.formatSliderValueToEditValue(self.deform_size_slider.value())))

    def updateActionButtons(self):
        self.build_guides_action_button.setEnabled(self.is_valid)
        self.build_static_action_button.setEnabled(self.is_valid)
        self.build_component_action_button.setEnabled(self.is_valid)
        self.connect_component_action_button.setEnabled(self.is_valid)

    def updateComponentName(self):
        self.component_name = self.component_name_edit.text()

    def setSceneModified(self):
        if not self.is_silent:
            self.node.scene.setModified(True)

    def formatSliderValueToEditValue(self, value):
        if value != 0:
            scaled_slider_value = round(value / 100, 2)
        else:
            scaled_slider_value = 0.01
        if CLASS_DEBUG: print("%s:: --formatSliderValue:: new Slider Value:: " % self.__class__.__name__, scaled_slider_value)
        return scaled_slider_value

    def formatSliderEditToSliderValue(self, text):
        slider_value_float = float(text)
        scaled_value = int(slider_value_float * 100)
        if CLASS_DEBUG: print("%s:: --formatSliderEditTextToFloat:: new Slider Value as int" % self.__class__.__name__, scaled_value)
        return scaled_value

    def onBuildGuides(self):
        if CLASS_DEBUG: print("BaseNodeProperties:_ --onBuildGuides ", self.node)
        if not self.is_disabled:
            self.node.guideBuild()

    def onBuildStatic(self):
        if CLASS_DEBUG: print("BaseNodeProperties:_ --onBuildStatic ", self.node)
        if not self.is_disabled:
            self.node.staticBuild()

    def onBuildComponent(self):
        if CLASS_DEBUG:  print("BaseNodeProperties:: --onBuildComponent: ", self.node)
        if not self.is_disabled:
            self.node.componentBuild()

    def onConnectComponents(self):
        if CLASS_DEBUG: print("BaseNodeProperties:: --onConnectComponent: ", self.node)
        if not self.is_disabled:
            self.node.connectComponent()

    def serialize(self):
        result_data = super().serialize()
        result_data['component_name'] = self.component_name
        result_data['is_disabled'] = self.is_disabled
        result_data['guide_size'] = self.guide_size
        result_data['deform_size'] = self.deform_size

        return result_data
    
    def deserialize(self, data, hashmap = {}, restore_id=True):
        result = super().deserialize(data, hashmap, restore_id)
        self.component_name_edit.setText(data['component_name'])
        self.disabled_checkbox.setChecked(data['is_disabled'])
        self.guide_slider_size_edit.setText(str(data['guide_size']))
        self.deform_slider_size_edit.setText(str(data['deform_size']))

        self.is_silent = False

        self.validateProperties()
        return True

class MNRB_Node(NodeEditorNode):
    operation_code = 0
    operation_title = "MNRB_Node"
    icon = None
    Node_Properties_Class = MNRB_NodeProperties

    def __init__(self, scene, inputs=[], outputs=[], color = MNRBColor.yellow.value):
        super().__init__(scene, self.__class__.operation_title, inputs, outputs)

        self.guide_component_hierarchy = None

        self._component_color = color

        self.guides = []
        self.controls = []
        self.deforms = []

        self.properties.connectHasBeenModifiedCallback(self.updateComponentHierarchyName)

    @property
    def component_color(self): return self._component_color
    @component_color.setter
    def component_color(self, value):
        if self._component_color != value:
            self._component_color = value

            self.setGuideColors()
        
        self._component_color = value

    def guideBuild(self) -> bool:
        self.guides = []

        if not self.scene.scene_rig_hierarchy.isGuideHierarchy():
            self.scene.scene_rig_hierarchy.createGuideHierarchy()
            current_guide_hierarchy = self.scene.scene_rig_hierarchy.getGuideHierarchyName()
            if CLASS_DEBUG: print("%s:: --guideBuild:: " % self.__class__.__name__, current_guide_hierarchy)
        else:
            current_guide_hierarchy = self.scene.scene_rig_hierarchy.getGuideHierarchyName()

        if self.guide_component_hierarchy is not None:
            if MC.objectExists(self.guide_component_hierarchy):
                MC.deleteObjectWithHierarchy(self.guide_component_hierarchy)

        current_component_guide_hierarchy_name = self.properties.component_name + GUIDE_HIERARCHY_SUFFIX
        current_component_guide_hierarchy = MC.createTransform(current_component_guide_hierarchy_name)
        if CLASS_DEBUG: print("%s:: --guideBuild:: Object to be parented: " % self.__class__.__name__, "Child:: ",current_component_guide_hierarchy, " Parent:: ", current_guide_hierarchy)
        MC.parentObject(current_component_guide_hierarchy, current_guide_hierarchy)
        self.guide_component_hierarchy = current_component_guide_hierarchy

        return True

    def staticBuild(self):
        raise NotImplementedError
    
    def componentBuild(self):
        raise NotImplementedError
    
    def connectComponent(self):
        raise NotImplementedError

    def updateComponentHierarchyName(self):
        if self.guide_component_hierarchy is not None:
            if MC.objectExists(self.guide_component_hierarchy):
                new_guide_component_hierarchy_name = self.properties.component_name + GUIDE_HIERARCHY_SUFFIX
                new_name = MC.renameObject(self.guide_component_hierarchy, new_guide_component_hierarchy_name)
                if new_name != self.guide_component_hierarchy:
                    self.guide_component_hierarchy = new_name
            else:
                if CLASS_DEBUG: print("%s:: --updateComponentHierarchyName:: ERROR:: trying to rename Component Hierarchy" % self.__class__.__name__)

    def setComponentGuideSize(self, size):
        for guide in self.guides:
            if CLASS_DEBUG: print("%s:: --setComponentGuideSize:: Setting Guide:: " % self.__class__.__name__, guide, " with object name: ", guide.name, " to Size:: ", size)
            if MC.objectExists(guide.name):
                guide.resize(size)

    def setComponentDeformRadius(self, size):
        for deform in self.deforms:
            if MC.objectExists(deform):
                MC.setJointRadius(deform, size)
    
    def setGuideColors(self):
        for guide in self.guides:
            guide.color = self.component_color

    def remove(self):
        super().remove()
        if CLASS_DEBUG: print("%s:: --remove:: current Guide_component_hierarchy:: " % self.__class__.__name__, self.guide_component_hierarchy)
        self.removeGuideHierarchyFromViewport()

    def removeGuideHierarchyFromViewport(self):
        if self.guide_component_hierarchy is not None:
            if MC.objectExists(self.guide_component_hierarchy):
                MC.deleteObjectWithHierarchy(self.guide_component_hierarchy)

    def serialize(self):
        result_data = super().serialize()
        result_data['operation_code'] = self.__class__.operation_code
        result_data['guide_component_hierarchy'] = self.guide_component_hierarchy

        guides = []
        for guide in self.guides: guides.append(guide.serialize())
        result_data['guides'] = guides

        return result_data
    
    def deserialize(self, data, hashmap={}, restore_id = True, exists=False):
        result = super().deserialize(data, hashmap, restore_id, exists)
        self.guide_component_hierarchy = data['guide_component_hierarchy']
    
        for guide_data in data['guides']:
            new_guide = guide(self, guide_data['name'], deserialized=True)
            new_guide.deserialize(guide_data, hashmap, restore_id)
            self.guides.append(new_guide)

        return True