import maya.cmds as cmds #type: ignore
from collections import Counter

class MC:
     
    @staticmethod
    def objectExists(object) -> bool:
        return cmds.objExists(object)

    @staticmethod
    def deleteObjectWithHierarchy(object):
        cmds.delete(object, hierarchy = "below")
        MC.clearSelection()

    @staticmethod
    def deleteNode(node):
        cmds.delete(node)
        MC.clearSelection()

    @staticmethod
    def renameObject(object, name) -> str:
        new_name = cmds.rename(object, name)
        MC.clearSelection()
        return new_name

    @staticmethod
    def findDuplicatesInNodeHiearchyByName(node, target_name) -> list:
        result = []

        all_nodes = cmds.listRelatives(node, allDescendents=True, fullPath=True)
        base_names = [cmds.ls(node)[0] for node in all_nodes]
        name_counts = Counter(base_names)
        
        target_count = name_counts.get(target_name, 0)

        if target_count > 0:
            result.append(target_name)
            result.append(target_count)

        MC.clearSelection()
        return result

    @staticmethod
    def getHierarchyContent(hierarchy_name) -> list:
        return cmds.listRelatives(hierarchy_name)

    @staticmethod
    def parentObject(child, parent):
        cmds.parent(child, parent)
        MC.clearSelection()

    @staticmethod
    def createTransform(name) -> str:
        new_transform = cmds.createNode("transform", name = name, skipSelect=True)
        MC.clearSelection()
        return new_transform

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
    
    @staticmethod
    def setLocatorLocalScale(locator, scale) -> None:
        locator_shape = MC.getObjectShapeNode(locator)
        cmds.setAttr(f"{locator_shape}.localScaleX", scale)
        cmds.setAttr(f"{locator_shape}.localScaleY", scale)
        cmds.setAttr(f"{locator_shape}.localScaleZ", scale)

    @staticmethod
    def listSourceConnections(node, attribute) -> list:
        return cmds.listConnections(f"{node}.{attribute}", source = True)
    
    @staticmethod
    def listDestinationConnections(node, attribute) -> list:
        return cmds.listConnections(f"{node}.{attribute}", destination = True)

    #joint specific methods
    @staticmethod
    def setJointRadius(joint, radius) -> None:
        cmds.setAttr(f"{joint}.radius", radius)

    #nurbs methods
    @staticmethod
    def createNurbsSphere(name) -> str:
        new_sphere = cmds.sphere(name = name)[0]
        MC.clearSelection()
        return new_sphere
    
    @staticmethod
    def setNurbsSphereShapeRadius(object, size) -> None:
        shape_node = MC.listSourceConnections(object, "create")[0]
        cmds.setAttr(f"{shape_node}.radius", size)
    
    #lambert methods
    @staticmethod
    def createLambertMaterial(name) -> str:
        return cmds.shadingNode("lambert", asShader=True, name = name)
    
    @staticmethod
    def setLambertColor(node, color):
        cmds.setAttr(f"{node}.color", color[0], color[1], color[2], type="double3")

    @staticmethod
    def setLambertTransparency(node, transparency: tuple):
        cmds.setAttr(f"{node}.transparency", transparency[0], transparency[1], transparency[2], type="double3")

    @staticmethod
    def setLambertAmbientColor(node, color: tuple):
        cmds.setAttr(f"{node}.ambientColor", color[0], color[1], color[2], type="double3")

    @staticmethod
    def setLambertIncandescence(node, incandescence: tuple):
        cmds.setAttr(f"{node}.incandescence", incandescence[0], incandescence[1], incandescence[2], type="double3")

    @staticmethod
    def createShaderSet(name) -> str:
        return cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name = name)

    @staticmethod
    def assignMaterialToShaderSet(material, shader_set):
        cmds.connectAttr(f"{material}.outColor", f"{shader_set}.surfaceShader", force=True)

    @staticmethod
    def assignObjectToShaderSet(object, shader):
        return cmds.sets(object, edit=True, forceElement=shader)
    
    @staticmethod
    def addStringAttribute(node_name, target_attribute, value, is_hidden) -> None:
        cmds.addAttr(node_name, dataType="string", longName = target_attribute, hidden = is_hidden)
        cmds.setAttr(f"{node_name}.{target_attribute}", value, type="string")

    @staticmethod
    def getAttribute(node_name, attribute_name) -> any:
        return cmds.getAttr(f"{node_name}.{attribute_name}")
    
    @staticmethod
    def getObjectWorldPositionMatrix(object_name) -> list:
        return cmds.xform(object_name, query =True, matrix = True, worldSpace=True)
    
    @staticmethod
    def setObjectWorldPositionMatrix(object_name, matrix):
        cmds.xform(object_name, matrix=matrix, worldSpace=True)

    @staticmethod
    def createJoint(name) -> str:
        new_joint = cmds.joint(name = name)
        MC.clearSelection()
        return new_joint
    
    @staticmethod
    def setJointPositionMatrix(name, matrix, world_space = True):
        cmds.xform(name, worldSpace=world_space, matrix = matrix)