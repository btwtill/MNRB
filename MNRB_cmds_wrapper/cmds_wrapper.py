import maya.cmds as cmds #type: ignore

class MC:
     
    @staticmethod
    def objectExists(object) -> bool:
        return cmds.objExists(object)

    @staticmethod
    def deleteObjectWithHierarchy(object):
        cmds.delete(object, hierarchy = "below")

    @staticmethod
    def renameObject(object, name) -> str:
        return cmds.rename(object, name)

    @staticmethod
    def parentObject(child, parent):
        cmds.parent(child, parent)

    @staticmethod
    def createTransform(name) -> str:
        return cmds.createNode("transform", name = name, skipSelect=True)

    @staticmethod
    def getFirstInViewPortSelection():
        result_selection = cmds.ls(sl=True)
        return result_selection[0] if result_selection != [] else None
    
    @staticmethod
    def clearSelection() -> None:
        cmds.select(clear=True)

    @staticmethod
    def getObjectShapeNode(object) -> str:
        return cmds.listRelatives(object, s=1)[0]

    @staticmethod
    def getObjectShapeNodes(object) -> list:
        return cmds.listRelatives(object, s=1)

    @staticmethod
    def setObjectDisplayColor(object, color) -> None:
        object_shape_node = MC.getObjectShapeNode(object)
        cmds.setAttr(f"{object_shape_node}.overrideEnabled", 1)
        cmds.setAttr(f"{object_shape_node}.overrideRGBColors", 1)
        cmds.setAttr(f"{object_shape_node}.overrideColorR", color[0])
        cmds.setAttr(f"{object_shape_node}.overrideColorG", color[1])
        cmds.setAttr(f"{object_shape_node}.overrideColorB", color[2])

    @staticmethod
    def createSpaceLocator(position) -> str:
        new_space_locator = cmds.spaceLocator(p=position)
        MC.clearSelection()
        return new_space_locator[0]
    
    @staticmethod
    def createSpaceLocator(position, name) -> str:
        new_space_locator = cmds.spaceLocator(p=position, name = name)
        MC.clearSelection()
        return new_space_locator[0]
    
    @staticmethod
    def createSpaceLocator(position, name) -> str:
        new_space_locator = cmds.spaceLocator(p=position, name = name)
        MC.clearSelection()
        return new_space_locator[0]
    
    @staticmethod
    def createSpaceLocator(position, name, color) -> str:
        new_space_locator = cmds.spaceLocator(p=position, name = name)
        MC.clearSelection()
        MC.setObjectDisplayColor(new_space_locator, color)
        return new_space_locator[0]
    
    #joint specific methods
    @staticmethod
    def setJointRadius(joint, radius) -> None:
        cmds.setAttr(f"{joint}.radius", radius)