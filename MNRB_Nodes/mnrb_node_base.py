import math
from PySide2.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QCheckBox, QSlider, QComboBox #type: ignore
from PySide2.QtCore import Qt #type: ignore
from PySide2.QtGui import QDoubleValidator #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_NodeProperties import NodeEditorNodeProperties #type: ignore
from MNRB.global_variables import GUIDE_HIERARCHY_SUFFIX, COMPONENT_ID_ATTRIBUTE_NAME, IDENITY_MATRIX #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_colors.colors import MNRBColor #type: ignore
from MNRB.MNRB_colors.colors import MNRBSceneColors #type: ignore
from MNRB.MNRB_naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_Nodes.property_UI_GraphicComponents.side_button import MirroringSidePrefixButton #type: ignore

CLASS_DEBUG = True
VALIDATE_DEBUG = True
GUIDE_DEBUG = True

class MNRB_NodeProperties(NodeEditorNodeProperties):
    def __init__(self, node):
        super().__init__(node)

        self.component_name = "Undefined"
        self.is_disabled = False
        self.is_silent = True

        self.guide_size = 1.0
        self.deform_size = 1.0

        self.is_guide_slider_edit_silent = False
        self.is_guide_slider_silent = False
        self.is_deform_slider_edit_silent = False
        self.is_deform_slider_silent = False

        self.updateActionButtons()

    def initUI(self):
        component_header_layout = QHBoxLayout()
        component_name_layout = QVBoxLayout()

        #component Name Label
        component_name_label = QLabel("Set Component Name:")
        component_name_label.setAlignment(Qt.AlignHCenter)
        component_name_layout.addWidget(component_name_label)

        #component Name
        self.component_name_edit = QLineEdit()
        self.component_name_edit.setPlaceholderText("Enter Component Name: ")
        self.component_name_edit.setAlignment(Qt.AlignCenter)
        self.component_name_edit.editingFinished.connect(self.updateComponentName)
        self.component_name_edit.editingFinished.connect(self.setHasBeenModified)
        component_name_layout.addWidget(self.component_name_edit)
        component_header_layout.addLayout(component_name_layout)

        #component Color
        self.component_color_dropdown = QComboBox()
        for color in MNRBColor:
            self.component_color_dropdown.addItem(color.name)
        self.component_color_dropdown.currentIndexChanged.connect(self.updateComponentColor)
        self.component_color_dropdown.currentIndexChanged.connect(self.setHasBeenModified)
        component_header_layout.addWidget(self.component_color_dropdown, alignment=Qt.AlignBottom)

        self.layout.addLayout(component_header_layout)

        #Side Index  
        side_prefix_layout = QHBoxLayout()
        self.left_prefix_button = MirroringSidePrefixButton(MNRB_Names.left.side)
        self.mid_prefix_button = MirroringSidePrefixButton(MNRB_Names.middle.side)
        self.right_prefix_button = MirroringSidePrefixButton(MNRB_Names.right.side)

        self.left_prefix_button.addButtonForDeselection(self.mid_prefix_button)
        self.left_prefix_button.addButtonForDeselection(self.right_prefix_button)

        self.right_prefix_button.addButtonForDeselection(self.mid_prefix_button)
        self.right_prefix_button.addButtonForDeselection(self.left_prefix_button)

        self.mid_prefix_button.addButtonForDeselection(self.right_prefix_button)
        self.mid_prefix_button.addButtonForDeselection(self.left_prefix_button)

        side_prefix_layout.addWidget(self.left_prefix_button)
        side_prefix_layout.addWidget(self.mid_prefix_button)
        side_prefix_layout.addWidget(self.right_prefix_button)

        self.layout.addLayout(side_prefix_layout)

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
        self.guide_slider_size_edit.editingFinished.connect(self.onGuideSizeEditChange)

        guide_slider_label_layout.addWidget(guide_size_slider_label)
        guide_slider_label_layout.addWidget(self.guide_slider_size_edit)

        self.layout.addLayout(guide_slider_label_layout)

        self.guide_size_slider = QSlider(Qt.Horizontal)
        self.guide_size_slider.setMinimum(0)
        self.guide_size_slider.setMaximum(10000)
        self.guide_size_slider.setValue(100)
        self.guide_size_slider.setTickPosition(QSlider.TicksBelow)
        self.guide_size_slider.setTickInterval(20)
        self.guide_size_slider.sliderReleased.connect(self.onGuideSliderChange)

        self.layout.addWidget(self.guide_size_slider)

        #deform Size Adjustment
        deform_slider_label_layout = QHBoxLayout()
        deform_size_slider_label = QLabel("Deform Size:")
        deform_size_slider_label.setAlignment(Qt.AlignCenter)
        deform_slider_label_layout.addWidget(deform_size_slider_label)

        self.deform_slider_size_edit = QLineEdit()
        self.deform_slider_size_edit.setText(str(1.0))
        self.deform_slider_size_edit.editingFinished.connect(self.onDeformSizeEditChange)

        deform_slider_label_layout.addWidget(deform_size_slider_label)
        deform_slider_label_layout.addWidget(self.deform_slider_size_edit)

        self.layout.addLayout(deform_slider_label_layout)

        self.deform_size_slider = QSlider(Qt.Horizontal)
        self.deform_size_slider.setMinimum(0)
        self.deform_size_slider.setMaximum(10000)
        self.deform_size_slider.setValue(100)
        self.deform_size_slider.setTickPosition(QSlider.TicksBelow)
        self.deform_size_slider.setTickInterval(20)
        self.deform_size_slider.sliderReleased.connect(self.onDeformSliderChange)

        self.layout.addWidget(self.deform_size_slider)

        self.layout.addStretch()
        self.connectHasBeenModifiedCallback(self.updateDisabledState)
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

        is_duplicate_component_name = False
        encounters = set()
        for node in self.node.scene.nodes:
            component_name = node.properties.component_name
            if component_name in encounters:
                is_duplicate_component_name = True
                break
            encounters.add(component_name)

        if is_duplicate_component_name:
            self.is_valid = False
            return False

        self.is_valid = True
        return True

    def validComponentName(self):
        if self.component_name_edit.text() != "" and self.component_name_edit.text() != "Undefined":
            return True
        else:
            return False

    def onGuideSizeEditChange(self):
        if not self.is_guide_slider_edit_silent:
            self.updateGuideSlider()
            self.updateGuideSize()

    def onGuideSliderChange(self):
        if not self.is_guide_slider_silent:
            self.updateGuideSliderSizeEdit()
            self.updateGuideSize()

    def onDeformSizeEditChange(self):
        if not self.is_deform_slider_edit_silent:
            self.updateDeformSlider()
            self.updateDeformSize()

    def onDeformSliderChange(self):
        if not self.is_deform_slider_silent:
            self.updateDeformSliderEdit()
            self.updateDeformSize()

    def updateGuideSize(self):
        #update the guide size valule
        self.guide_size = float(self.guide_slider_size_edit.text())
        #call the nodes guide resize funcion
        if CLASS_DEBUG: print("%s:: --updateGuideSize:: Setting Guide Size To: " % self.__class__.__name__, self.guide_size)
        if CLASS_DEBUG: print("%s:: --updateGuideSize:: of Node::  " % self.__class__.__name__, self.node)
        self.node.setComponentGuideSize(self.guide_size)
        #set properties to be modified
        self.setHasBeenModified()

    def updateDeformSize(self):
        self.deform_size = float(self.deform_slider_size_edit.text())
        if CLASS_DEBUG: print("%s:: --updateDeformSize:: Setting Deform Size To: " % self.__class__.__name__, self.deform_size)
        if CLASS_DEBUG: print("%s:: --updateDeformSize:: of Node::  " % self.__class__.__name__, self.node)
        self.node.setComponentDeformRadius(self.deform_size)
        self.setHasBeenModified()

    def updateDisabledState(self):
        self.is_disabled = self.disabled_checkbox.isChecked()

    def updateGuideSlider(self):
        self.is_guide_slider_silent = True
        self.guide_size_slider.setValue(self.formatSliderEditToSliderValue(self.guide_slider_size_edit.text()))
        self.is_guide_slider_silent = False

    def updateGuideSliderSizeEdit(self):#
        self.is_guide_slider_edit_silent = True
        self.guide_slider_size_edit.setText(str(self.formatSliderValueToEditValue(self.guide_size_slider.value())))
        self.is_guide_slider_edit_silent = False

    def updateDeformSlider(self):
        self.is_deform_slider_silent = True
        self.deform_size_slider.setValue(self.formatSliderEditToSliderValue(self.deform_slider_size_edit.text()))
        self.is_deform_slider_silent = False

    def updateDeformSliderEdit(self):
        self.is_deform_slider_edit_silent = True
        self.deform_slider_size_edit.setText(str(self.formatSliderValueToEditValue(self.deform_size_slider.value())))
        self.is_deform_slider_edit_silent = False

    def updateActionButtons(self):
        self.build_guides_action_button.setEnabled(self.is_valid)
        self.build_static_action_button.setEnabled(self.is_valid)
        self.build_component_action_button.setEnabled(self.is_valid)
        self.connect_component_action_button.setEnabled(self.is_valid)

    def updateComponentName(self):
        if CLASS_DEBUG: print("%s:: --updateComponentName:: Live Fetch from Line Edit:: " % self.__class__.__name__, self.component_name_edit.text())
        self.component_name = self.component_name_edit.text()
        if CLASS_DEBUG: print("%s:: --updateComponentName:: self.component_name:: " % self.__class__.__name__, self.component_name)
        self.node.title = self.component_name
        self.node.updateGuideComponentHierarchyName()

    def updateComponentColor(self, index):
        if CLASS_DEBUG: print("%s:: --updateComponentColor:: Setting Color To: " % self.__class__.__name__, self.component_color_dropdown.itemText(index))
        if CLASS_DEBUG: print("%s:: --updateComponentColor:: Setting Color To: " % self.__class__.__name__, MNRBSceneColors.mapColorNameToColor(self.component_color_dropdown.itemText(index)))
        self.node.component_color = MNRBSceneColors.mapColorNameToColor(self.component_color_dropdown.itemText(index))

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

        if CLASS_DEBUG: print("%s:: --deserialize:: deserializing component_name:: " % self.__class__.__name__, data['component_name'])
        self.component_name_edit.setText(data['component_name'])
        if CLASS_DEBUG: print("%s:: --deserialize:: deserializing component disabled:: "% self.__class__.__name__, data['is_disabled'])
        self.disabled_checkbox.setChecked(data['is_disabled'])
        if CLASS_DEBUG: print("%s:: --deserialize:: deserializing guide Size:: "% self.__class__.__name__, data['guide_size'])
        self.guide_slider_size_edit.setText(str(data['guide_size']))
        if CLASS_DEBUG: print("%s:: --deserialize:: deserializing deform Size:: "% self.__class__.__name__, data['deform_size'])
        self.deform_slider_size_edit.setText(str(data['deform_size']))

        if CLASS_DEBUG: print("%s:: --deserialize:: updating guide Size Edit "% self.__class__.__name__)
        self.onGuideSizeEditChange()
        self.is_silent = False

        if CLASS_DEBUG: print("%s:: --deserialize:: updating component Name "% self.__class__.__name__)
        self.updateComponentName()
        self.node.setComponentGuideHiearchyName()
        
        if CLASS_DEBUG: print("%s:: --deserialize:: validate Properties "% self.__class__.__name__)
        self.validateProperties()
        return True

class MNRB_Node(NodeEditorNode):
    operation_code = 0
    operation_title = "MNRB_Node"
    icon = None
    Node_Properties_Class = MNRB_NodeProperties
    
    guide_count = 0

    def __init__(self, scene, inputs=[], outputs=[], color = MNRBColor.yellow):
        super().__init__(scene, self.__class__.operation_title, inputs, outputs)

        self._guide_component_hierarchy = None

        self._component_color = color

        self.guides = []
        self.guide_positions = []

        self.controls = []
        self.deforms = []

        self.is_guide_build = False
        self.is_static_build = False
        self.is_comonent_build = False
        self.is_connected = False

        self.is_silent =  False
        self.reconstruct_guides = False

    @property
    def guide_component_hierarchy(self): return self._guide_component_hierarchy
    @guide_component_hierarchy.setter
    def guide_component_hierarchy(self, value):
        print(value)
        self._guide_component_hierarchy = value

    @property
    def component_color(self): return self._component_color
    @component_color.setter
    def component_color(self, value):
        if self._component_color != value:
            self._component_color = value
            if CLASS_DEBUG: print("%s:: --component_color:: Setting new Component Color:: " % self.__class__.__name__, value)
            self.setGuideColors()
        
        self._component_color = value

    def guideBuild(self) -> bool:
        if self.scene.virtual_rig_hierarchy.guide_hierarchy_object.ensureExistence():
            current_guide_hierarchy = self.scene.virtual_rig_hierarchy.guide_hierarchy_object.name
        else:
            if CLASS_DEBUG: print("%s:: --guideBuild:: Error Ensuring the Guide Hierarchy: " % self.__class__.__name__)
            return False

        current_component_guide_hierarchy_name = self.properties.component_name + GUIDE_HIERARCHY_SUFFIX

        if MC.objectExists(current_component_guide_hierarchy_name):
            if CLASS_DEBUG: print("%s:: --guideBuild:: Guide Hierarchy Already Exists: " % self.__class__.__name__)
            self.reconstruct_guides = True
            self.guide_positions = []
            for guide in self.guides:
                if CLASS_DEBUG: print("%s:: --guideBuild:: Collecting guide Positions for: " % self.__class__.__name__, self.guides)
                if guide.exists():
                    self.guide_positions.append(guide.getPosition())
                else:
                    self.guide_positions.append(IDENITY_MATRIX)
            MC.deleteObjectWithHierarchy(current_component_guide_hierarchy_name)
        else: 
            self.reconstruct_guides = False
            self.guide_positions = []

        self.guides = []

        current_component_guide_hierarchy = MC.createTransform(current_component_guide_hierarchy_name)
        self.addComponentIdLink(current_component_guide_hierarchy)

        if CLASS_DEBUG: print("%s:: --guideBuild:: Object to be parented: " % self.__class__.__name__, "Child:: ",current_component_guide_hierarchy, " Parent:: ", current_guide_hierarchy)
        MC.parentObject(current_component_guide_hierarchy, current_guide_hierarchy)
        self.guide_component_hierarchy = current_component_guide_hierarchy

        return True

    def staticBuild(self):
        if self.scene.virtual_rig_hierarchy.rig_hierarchy_object.ensureExistence():
            current_rig_hierarchy = self.scene.virtual_rig_hierarchy.rig_hierarchy_object.name
            if self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.ensureExistence():
                current_skeleton_hierarchy = self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name
        else:
            if CLASS_DEBUG: print("%s:: --guideBuild:: Error Ensuring the Guide Hierarchy: " % self.__class__.__name__)
            return False
        
        self.deforms = []

        return True
    
    def componentBuild(self):
        raise NotImplementedError
    
    def connectComponent(self):
        raise NotImplementedError

    def addComponentIdLink(self, object):
        MC.addStringAttribute(object, COMPONENT_ID_ATTRIBUTE_NAME, str(self.id), True)

    def validateComponentIdLink(self, object):
        component_id_attribute = MC.getAttribute(object, COMPONENT_ID_ATTRIBUTE_NAME)
        if component_id_attribute is not None:
            if int(component_id_attribute) == self.id:
                return True
            else:
                return False
        else:
            return False

    def updateGuideComponentHierarchyName(self):
        if GUIDE_DEBUG: print("%s:: --updateComponentHierarchyName:: Calling Update Guide Component Hierarchy Name: " % self.__class__.__name__)
        
        if self.is_silent:
            return
        
        if GUIDE_DEBUG: print("%s:: --updateComponentHierarchyName:: Current Guide Hierarchy Name: " % self.__class__.__name__, self.guide_component_hierarchy)

        if self.guide_component_hierarchy is not None:
            if not MC.objectExists(self.guide_component_hierarchy):
                if GUIDE_DEBUG: print("%s:: --updateComponentHierarchyName:: ERROR:: trying to rename Component Hierarchy" % self.__class__.__name__)
                self.setComponentGuideHiearchyName()
                return

            if GUIDE_DEBUG: print("%s:: --updateComponentHierarchyName:: Component Name Variable:: " % self.__class__.__name__, self.properties.component_name)
            if GUIDE_DEBUG: print("%s:: --updateComponentHierarchyName:: Old Component Name:: " % self.__class__.__name__, self.guide_component_hierarchy)

            has_duplicate_name = False

            new_guide_component_hierarchy_name = self.properties.component_name + GUIDE_HIERARCHY_SUFFIX

            is_same_name = new_guide_component_hierarchy_name == self.guide_component_hierarchy
            if is_same_name:
                return
            
            duplicate_name = MC.findDuplicatesInNodeHiearchyByName(self.scene.virtual_rig_hierarchy.guide_hierarchy_object.name, new_guide_component_hierarchy_name)
            if GUIDE_DEBUG: print("%s:: --updateComponentHierarchyName:: found Duplicate Names:: " % self.__class__.__name__, duplicate_name)

            has_valid_component_id = self.validateComponentIdLink(self.guide_component_hierarchy)

            if duplicate_name != []:
                has_duplicate_name = True
                if GUIDE_DEBUG: print("%s:: --updateComponentHierarchyName:: setting has_duplicate_names to:: " % self.__class__.__name__, has_duplicate_name)
                new_guide_component_hierarchy_name = new_guide_component_hierarchy_name + str(duplicate_name[1])

            if GUIDE_DEBUG: print("%s:: --updateComponentHierarchyName:: new Name:: " % self.__class__.__name__, new_guide_component_hierarchy_name)
            
            if has_valid_component_id:
                new_name = MC.renameObject(self.guide_component_hierarchy, new_guide_component_hierarchy_name)
                if GUIDE_DEBUG: print("%s:: --updateComponentHierarchyName:: has been renamed to:: " % self.__class__.__name__, new_name)
                self.guide_component_hierarchy = new_name
                
                if GUIDE_DEBUG: print("%s:: --updateComponentHierarchyName::  updating Names for guides:: " % self.__class__.__name__, self.guides)
                for guide in self.guides:
                    guide.updateName(self.properties.component_name, has_duplicate_name)
            else:
                self.setComponentGuideHiearchyName()

    def setComponentGuideHiearchyName(self):
        if CLASS_DEBUG: print("%s:: --setComponentGuideHierarchyName:: guide Hierarchy name Old:: " % self.__class__.__name__, self.guide_component_hierarchy, " New:: ", self.properties.component_name + GUIDE_HIERARCHY_SUFFIX )
        self.guide_component_hierarchy = self.properties.component_name + GUIDE_HIERARCHY_SUFFIX
        if CLASS_DEBUG: print("%s:: --setComponentGuideHierarchyName:: New Guide Hierarchy Name:: " % self.__class__.__name__, self.guide_component_hierarchy)

    def reconstructGuides(self):
        if self.reconstruct_guides:
            if CLASS_DEBUG: print("%s:: --reconstructGuides:: Guide Positions to be reconstructed::" % self.__class__.__name__, self.guide_positions)

            for index, guide in enumerate(self.guides):
                guide.setPosition(self.guide_positions[index])

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
        if CLASS_DEBUG: print("%s:: --setGuideColors:: setting Guide Color for Guides:" % self.__class__.__name__, self.guides)
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
        result_data['component_color'] = self.component_color.name
        guides = []
        for guide in self.guides: guides.append(guide.serialize())
        result_data['guides'] = guides

        return result_data
    
    def deserialize(self, data, hashmap={}, restore_id = True, exists=False):
        result = super().deserialize(data, hashmap, restore_id, exists)

        self.setComponentGuideHiearchyName()

        self.component_color = MNRBSceneColors.mapColorNameToColor(data['component_color'])

        self.is_silent = True
        self.properties.is_silent = True
        self.properties.component_color_dropdown.setCurrentText(data['component_color'])
        self.properties.is_silent = False
        self.is_silent = False

        for guide_data in data['guides']:
            new_guide = guide(self, guide_data['name'], deserialized=True)
            new_guide.deserialize(guide_data, hashmap, restore_id)
            self.guides.append(new_guide)

        return True