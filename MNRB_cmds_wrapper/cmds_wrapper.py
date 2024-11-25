import maya.cmds as cmds #type: ignore

class MC:
     
    @staticmethod
    def getFirstInViewPortSelection():
        return cmds.ls(sl=True)[0]