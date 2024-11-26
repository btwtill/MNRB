from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.global_variables import GUIDE_SUFFIX, RIG_SUFFIX #type: ignore

class MNRB_Scene_Hirarchy():
    def __init__(self, scene, guide_suffix = GUIDE_SUFFIX, rig_suffix = RIG_SUFFIX) -> None:
        self.scene = scene

        self.guide_suffix = guide_suffix
        self.rig_suffix = rig_suffix

        self.guide_hirarchy = None
        self.rig_hirarchy = None

    def createGuideHirarchy(self):
        self.guide_hirarchy = MC.createTransform(self.scene.getSceneRigName() + self.guide_suffix)

    def createRigHirarchy(self):
        self.rig_hirarchy = MC.createTransform(self.scene.getSceneRigName() + self.rig_suffix)

    def isGuideHirarchy(self):
        return MC.objectExists(self.guide_hirarchy)
    
    def isRigHirarchy(self):
        return MC.objectExists(self.rig_hirarchy)