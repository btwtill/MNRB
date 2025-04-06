from PySide2.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QCheckBox, QSlider, QComboBox #type: ignore
from PySide2.QtCore import Qt #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node #type: ignore
from MNRB.MNRB_Colors.colors import MNRBColor #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_MULTIDEFORMCOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_Deform.deform import deform #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

GUIDE_DEBUG = True
CLASS_DEBUG = True

class MNRB_Node_MultiDeformComponent_Properties(MNRB_NodeProperties): 

    def __init__(self, node):
        super().__init__(node)

        self.last_deform_count = 0
        self.current_deform_count  = 0
        self.auto_orient = True

    def initUI(self):
        super().initUI()

        deform_count_layout = QVBoxLayout()
        self.deform_count_slider_label_text = "Number of Deforms in Chain: \t"
        self.deform_count_slider_label = QLabel(self.deform_count_slider_label_text)

        self.deform_count_slider = QSlider(Qt.Horizontal)
        self.deform_count_slider.setMaximum(20)
        self.deform_count_slider.setMinimum(0)
        self.deform_count_slider.setSingleStep(1)
        self.deform_count_slider.valueChanged.connect(self.updateDeformCountSliderLabel)
        self.deform_count_slider.sliderReleased.connect(self.updateDeformCount)
        
        deform_count_layout.addWidget(self.deform_count_slider_label)
        deform_count_layout.addWidget(self.deform_count_slider)
        
        self.layout.addLayout(deform_count_layout)

        chain_orientation_label = QLabel("OrientChain")

        auto_orientation_label = QLabel("Auto_Orient")


    def updateDeformCountSliderLabel(self, silent = False):
        self.last_deform_count = self.current_deform_count
        self.deform_count_slider_label.setText(self.deform_count_slider_label_text + str(self.deform_count_slider.value()))
        self.current_deform_count = self.deform_count_slider.value()

    def updateDeformCount(self, silent = False):
        if not self.is_silent:
            if CLASS_DEBUG: print("%s::updateDeformCount:: Properties are Silent::" % self.__class__.__name__, self.is_silent)
            if CLASS_DEBUG: print("%s::updateDeformCount:: About to update Deform Count" % self.__class__.__name__)
            self.node.onDeformCountSliderChange()

    def serialize(self):
        result_data = super().serialize()
        result_data["number_of_deforms"] = self.current_deform_count
        return result_data
    
    def deserialize(self, data, hashmap = {}, restore_id=True):
        result = super().deserialize(data, hashmap, restore_id)
        self.is_silent = True
        self.deform_count_slider.setValue(data["number_of_deforms"])
        self.is_silent = False
        return True

@registerNode(OPERATIONCODE_MULTIDEFORMCOMPONENT)
class MNRB_Node_MultiDeformComponent(MNRB_NodeTemplate):
    operation_code = OPERATIONCODE_MULTIDEFORMCOMPONENT
    operation_title = "Multi_Def"
    icon = ""

    Node_Properties_Class = MNRB_Node_MultiDeformComponent_Properties

    def __init__(self, scene,
                inputs = [["parent_ctrl", SocketTypes.srt, False], ["parent_def", SocketTypes.deform, False]], 
                outputs=[
                        ["start", SocketTypes.srt, True], ["start", SocketTypes.deform, True],
                        ],
                color=MNRBColor.yellow):
        super().__init__(scene, inputs, outputs, color)


    def guideBuild(self):
        if not super().guideBuild():
            return False
        
        if GUIDE_DEBUG: print("%s:: Building Guides:: " % self.__class__.__name__, self)

        self.multi_Def_Chain_start_guide = guide(self, name = "start")
        MC.parentObject(self.multi_Def_Chain_start_guide.name, self.guide_component_hierarchy)

        amount_of_extra_guides = self.properties.current_deform_count

        for index in range(amount_of_extra_guides):
            
            new_guide_name = str(index)

            self.addGuideToChain(new_guide_name)

        self.reconstructGuides()
    
    def staticBuild(self):
        if not super().staticBuild():
            return False
        
        for index, guide in enumerate(self.guides):
            guide_pos = guide.getPosition()

            new_deform = deform(self, guide.guide_name)
            new_deform.setPosition(guide_pos)

            if index > 0:
                parent_deform = self.deforms[index - 1]
                MC.parentObject(new_deform.name, parent_deform.name)
            else:
                MC.parentObject(new_deform.name, self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name)
    
    def componentBuild(self):
        return super().componentBuild()

    def connectComponent(self):
        return super().connectComponent()
    
    def onDeformCountSliderChange(self):
        if CLASS_DEBUG: 
            print("%s ::onDeformCountSliderChange::current deform count from Slider::" % self.__class__.__name__, self.properties.current_deform_count)
            print("%s ::onDeformCountSliderChange::actual registered deforms::" % self.__class__.__name__, len(self.outputs))
            print("%s:: onDeformCountSliderChange:: " % self.__class__.__name__, " old deform count ", self.properties.last_deform_count)
            print("%s:: onDeformCountSliderChange:: " % self.__class__.__name__, " new deform count ", self.properties.current_deform_count)

        #get overall amount of deforms 
        current_deform_count = int((len(self.outputs) - 2) / 2)

        if self.properties.current_deform_count > self.properties.last_deform_count:

            if GUIDE_DEBUG: 
                    print("%s:: addGuideFromChain:: " % self.__class__.__name__, " current length of guides:: ", len(self.guides))
                    print("%s:: addGuideFromChain:: " % self.__class__.__name__, " amount to be add ", current_deform_count - self.properties.current_deform_count)
                    print("%s:: addGuideFromChain:: " % self.__class__.__name__, " old deform count ", self.properties.last_deform_count)
                    print("%s:: addGuideFromChain:: " % self.__class__.__name__, " new deform count ", self.properties.current_deform_count)

            for guide_amount in range(self.properties.current_deform_count - current_deform_count):

                new_guide_name = str(current_deform_count + guide_amount)
                if CLASS_DEBUG: print("%s::New Guide Name:: " % self.__class__.__name__, new_guide_name)

                #create new output socket for chain
                self.addOutputSocket(output_type = 1, output_socket_value = new_guide_name, is_output_multi_edged = True)
                self.addOutputSocket(output_type = 2, output_socket_value = new_guide_name, is_output_multi_edged = True)

                if self.isAllGuidesExistend():
                    self.addGuideToChain(new_guide_name)

        else:

            #remove the last two sockets
            if current_deform_count >= 1:
                if GUIDE_DEBUG: 
                    print("%s:: removeGuideFromChain:: " % self.__class__.__name__, " current length of guides:: ", len(self.guides))
                    print("%s:: removeGuideFromChain:: " % self.__class__.__name__, " amount to be removed ", current_deform_count - self.properties.current_deform_count)
                    print("%s:: removeGuideFromChain:: " % self.__class__.__name__, " old deform count ", self.properties.last_deform_count)
                    print("%s:: removeGuideFromChain:: " % self.__class__.__name__, " new deform count ", self.properties.current_deform_count)

                for guide_amount in range(current_deform_count - self.properties.current_deform_count):
                    self.removeLastSocket()
                    self.removeLastSocket()

                    if self.isAllGuidesExistend():
                        self.removeGuideFromChain()

    def addGuideToChain(self, new_guide_name):
        if CLASS_DEBUG: 
            print("%s:: addGuideToChain:: " % self.__class__.__name__)
            print("%s:: addGuideToChain:: with name" % self.__class__.__name__, new_guide_name)

        #parent guide
        parent_guide = self.guides[-1]

        if CLASS_DEBUG: 
            print("%s:: addGuideToChain:: parent guide:: " % self.__class__.__name__, parent_guide)
            print("%s:: addGuideToChain:: parent guide Name:: " % self.__class__.__name__, parent_guide.name)

        #create new guide with that name
        new_guide = guide(self, new_guide_name, parent_guide)

        #get last guide position 
        new_guide.setPosition(parent_guide.getPosition())
        
        #parent guide
        MC.parentObject(new_guide.name, parent_guide.name)

        #set new guide position
        MC.addTranslation(new_guide.name, 5.0, 0.0, 0.0)

    def removeGuideFromChain(self):
        if GUIDE_DEBUG: print("%s:: removeGuideFromChain:: " % self.__class__.__name__)
        
        last_guide_in_chain = self.guides.pop()
        last_guide_in_chain.remove()