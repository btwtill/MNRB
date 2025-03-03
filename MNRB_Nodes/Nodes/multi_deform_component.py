from PySide2.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QCheckBox, QSlider, QComboBox #type: ignore
from PySide2.QtCore import Qt #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node #type: ignore
from MNRB.MNRB_Colors.colors import MNRBColor #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_MULTIDEFORMCOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

GUIDE_DEBUG = True
CLASS_DEBUG = True

class MNRB_Node_MultiDeformComponent_Properties(MNRB_NodeProperties): 

    def __init__(self, node):
        super().__init__(node)

        self.last_deform_count = 0
        self.current_deform_count  = 0

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
        
        deform_count_layout.addWidget(self.deform_count_slider_label)
        deform_count_layout.addWidget(self.deform_count_slider)
        
        self.layout.addLayout(deform_count_layout)

    def updateDeformCountSliderLabel(self, silent = False):
        self.last_deform_count = self.current_deform_count
        self.deform_count_slider_label.setText(self.deform_count_slider_label_text + str(self.deform_count_slider.value()))
        self.current_deform_count = self.deform_count_slider.value()
        if not self.is_silent:
            if CLASS_DEBUG: print("%s::updateDeformCountSliderLabel:: Properties are Silent::" % self.__class__.__name__, self.is_silent)
            if CLASS_DEBUG: print("%s::updateDeformCountSliderLabel:: About to update Deform Count" % self.__class__.__name__)
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
                        ["chain_start", SocketTypes.srt, True], ["chain_start", SocketTypes.deform, True],
                        ["chain_end", SocketTypes.srt, True], ["chain_end", SocketTypes.deform, True],
                        ], 
                color=MNRBColor.yellow):
        super().__init__(scene, inputs, outputs, color)

    def onDeformCountSliderChange(self):
        if self.properties.current_deform_count > self.properties.last_deform_count:
            self.addGuideToChain()
        else:
            self.removeGuideFromChain()

    def addGuideToChain(self):
        if GUIDE_DEBUG: print("%s:: addGuideToChain:: " % self.__class__.__name__)
        self.addOutputSocket(output_type = 2, output_socket_value = "test", is_output_multi_edged = False)

    def removeGuideFromChain(self):
        if GUIDE_DEBUG: print("%s:: removeGuideFromChain:: " % self.__class__.__name__)

    def guideBuild(self):
        if not super().guideBuild():
            return False
        
        if GUIDE_DEBUG: print("%s:: Building Guides:: " % self.__class__.__name__, self)

        self.multi_Def_Chain_start_guide = guide(self, name = "chain_start")
        MC.parentObject(self.multi_Def_Chain_start_guide.name, self.guide_component_hierarchy)

        self.reconstructGuides()
    
    def staticBuild(self):
        return super().staticBuild()

    def componentBuild(self):
        return super().componentBuild()

    def connectComponent(self):
        return super().connectComponent()