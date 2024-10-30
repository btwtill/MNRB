import maya.cmds as cmds
from MNRB.functionLibrary import generalFunctions as gf
from MNRB import autolibGlobalVariables as gVar


def createSimpleFKArmComponentGuides(rigName, color = [0, 0, 1], forwardAxies = "X", distance = 1):
    cmpntName = "arm"
    cmpntColor = color
     
    guideHirarchy = cmds.createNode("transform", name = f"{gVar.LEFTDECLARATION}_{rigName}_guide_hrc", parent = f"{rigName}_guide_hrc")

    guides = gf.createGuideChainNumBased(4, cmpntName, 
                                         side = gVar.LEFTDECLARATION, 
                                         color = cmpntColor,
                                         defaultDist = distance,
                                         defaultforwardAxies = forwardAxies,
                                          baseName = cmpntName)
    
    print(guides[0])

    cmds.parent(f"{gVar.LEFTDECLARATION}_{cmpntName}_{guides[0]}_guide_srt", guideHirarchy)
    
    return guides, guideHirarchy

def createSimpleFKArmComponentSkeleton(guideHirarchy, cmpntDeformHirarchy):
    guides = cmds.listRelatives(guideHirarchy, children=True)

    joints = []

    for index, guide in enumerate(guides):

        newJoint = cmds.joint(name = f"{guide.replace('srt', 'skn')}")
        
        joints.append(newJoint)

        guidePosMtx = cmds.xform(guide, query = True, m = True, ws = True)

        cmds.xform(newJoint, m = guidePosMtx, ws = True)

        if index - 1 >= 0:
            cmds.parent(newJoint, joints[index - 1])
        else:
            cmds.parnet(newJoint, cmpntDeformHirarchy)
    
    return joints


def createSimpleFKArmComponent(rigName, guideDir, jointParent ):
    pass