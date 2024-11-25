import maya.cmds as cmds #type: ignore

class MC:
     
    @staticmethod
    def getFirstInViewPortSelection():
        result_selection = cmds.ls(sl=True)
        return result_selection[0] if result_selection != [] else None