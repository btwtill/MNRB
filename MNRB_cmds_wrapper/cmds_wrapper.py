import maya.cmds as cmds #type: ignore

class MC:
     
    @staticmethod
    def getFirstInViewPortSelection():
        result_selection = cmds.ls(sl=True)
        return result_selection[0] if result_selection != [] else None
    
    @staticmethod
    def createSpaceLocator(position):
        new_space_locator = cmds.spaceLocator(p=position)
        return new_space_locator