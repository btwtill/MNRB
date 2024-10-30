import maya.cmds as cmds
from MNRB.functionLibrary import generalFunctions as gf
from MNRB import autolibGlobalVariables as gVar


def createSimpleFKSpineComponentGuides(rigName, 
                                       color = [1, 1, 0], 
                                       forwardAxies = "X", 
                                       distance = 1):
    cmpntName = "spine"
    cmpntColor = color
    
    guideHirarchy = cmds.createNode("transform", name = f"{gVar.CENTERDECLARATION}_{rigName}_guide_hrc", parent = f"{rigName}_guide_hrc")

    guides = gf.createGuideChainNumBased(4, cmpntName, 
                                         side = gVar.CENTERDECLARATION, 
                                         color = cmpntColor,
                                         defaultDist = distance,
                                         defaultforwardAxies = forwardAxies,
                                         baseName = cmpntName)
    
    print(guides[0])

    cmds.parent(f"{gVar.CENTERDECLARATION}_{cmpntName}_{guides[0]}_guide_srt", guideHirarchy)
    
    return guides, guideHirarchy