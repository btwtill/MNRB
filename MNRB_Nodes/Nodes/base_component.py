from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_BASECOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.MNRB_Deform.deform import deform #type: ignore
from MNRB.MNRB_Controls.control import control #type: ignore

GUIDE_DEBUG = True

class MNRB_Node_BaseComponent_Properties(MNRB_NodeProperties):
        
    def serialize(self):
        result_data = super().serialize()
        return result_data
    
    def deserialize(self, data, hashmap = {}, restore_id=True):
        result = super().deserialize(data, hashmap, restore_id)
        return True

@registerNode(OPERATIONCODE_BASECOMPONENT)
class MNRB_Node_BaseComponent(MNRB_NodeTemplate):
    operation_code = OPERATIONCODE_BASECOMPONENT
    operation_title = "Base"
    icon = ""

    Node_Properties_Class = MNRB_Node_BaseComponent_Properties

    def __init__(self, scene):
        super().__init__(scene, inputs = [], outputs=[["base_ctrl", SocketTypes.srt, True], ["base_def", SocketTypes.deform, True]])

    def guideBuild(self):
        if GUIDE_DEBUG: print("%s:: Building Guides:: " % self.__class__.__name__, self)

        if not super().guideBuild():
            return False

        base_component_guide = guide(self, name = "global")
        MC.parentObject(base_component_guide.name, self.guide_component_hierarchy)

        self.reconstructGuides()
        
    def staticBuild(self):
        print("%s:: Building Static:: " % self)
        if not super().staticBuild():
            return False
        
        guide_pos = self.guides[0].getPosition()

        base_deform = deform(self, "base")
        MC.setJointPositionMatrix(base_deform.name, guide_pos)
        MC.parentObject(base_deform.name, self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name)
        
        return True
    
    def componentBuild(self):
        print("%s:: Building Component:: " % self)
        if not super().componentBuild():
            return False
        
        guide_pos = self.guides[0].getPosition(reset_scale = False)

        base_control = control(self, "base")
        base_control.setPosition(guide_pos)

        MC.parentObject(base_control.name, self.control_hierarchy)
    
    def connectComponent(self):
        print("%s:: Connecting Component:: " % self)