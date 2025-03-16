import maya.cmds as cmds #type: ignore
import maya.api.OpenMaya as om #type: ignore
import maya.mel as mel #type:ignore
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
    def deleteNodeHistory(node):
        cmds.delete(node, constructionHistory=True)

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
    def parentShape(shape, parent):
        cmds.parent(shape, parent, shape=True, relative=True)
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
    def isSelectionClear() -> bool:
        return True if cmds.ls(sl=True) == [] else False

    @staticmethod
    def selectObject(node_name):
        if MC.isSelectionClear():
            cmds.select(node_name)
        else:
            cmds.select(node_name, add=True)

    @staticmethod
    def selectNode(node_name):
        MC.selectObject

    @staticmethod
    def getObjectShapeNode(object) -> str:
        return cmds.listRelatives(object, s=1)[0]

    @staticmethod
    def getObjectShapeNodes(object) -> list:
        return cmds.listRelatives(object, s=1)
    
    @staticmethod
    def getObjectParentNode(object) -> list:
        parent_node = cmds.listRelatives(object, parent=True)
        MC.clearSelection()
        return parent_node

    @staticmethod
    def setShapeNodeColor(shape_node, color):
        cmds.setAttr(f"{shape_node}.overrideEnabled", 1)
        cmds.setAttr(f"{shape_node}.overrideRGBColors", 1)
        cmds.setAttr(f"{shape_node}.overrideColorR", color[0])
        cmds.setAttr(f"{shape_node}.overrideColorG", color[1])
        cmds.setAttr(f"{shape_node}.overrideColorB", color[2])

    @staticmethod
    def setObjectDisplayColor(object, color) -> None:
        object_shape_node = MC.getObjectShapeNode(object)
        MC.setShapeNodeColor(object_shape_node, color)

    @staticmethod
    def setDisplayType(node, display_type) -> None:
        MC.setAttribute(node, "overrideEnabled", 1)
        if display_type == "normal" or display_type == "Normal":
            MC.setAttribute(node, "overrideDisplayType", 0)
        if display_type == "template" or display_type == "Template":
            MC.setAttribute(node, "overrideDisplayType", 1)
        if display_type == "reference" or display_type == "Reference":
            MC.setAttribute(node, "overrideDisplayType", 2)

    @staticmethod
    def setOverrideVisibility(node, state = False) -> bool:
        MC.setAttribute(node, "overrideEnabled", 1)
        MC.setAttribute(node, "overrideVisibility", state)

        return MC.getAttribute(node, "overrideVisibility")

    @staticmethod
    def hideInOutliner(node) -> bool:
        MC.setAttribute(node, "hiddenInOutliner", 1)
        return MC.getAttribute(node, "hiddenInOutliner")

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

    @staticmethod
    def createNurbsCircle(name, x_normal = 0, y_normal = 1, z_normal = 0):
        new_circle = cmds.circle(name = name, normalX = 0, normalY = 1, normalZ = 0)
        MC.clearSelection()
        return new_circle[0]
    
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
    def connectAttribute(source_node, source_attribute_name, target_node, target_attribute, force=False):
        cmds.connectAttr(f"{source_node}.{source_attribute_name}", f"{target_node}.{target_attribute}", force = force)

    @staticmethod
    def disconnectAttribute(source_node, source_attribute_name, target_node, target_attribute):
        cmds.disconnectAttr(f"{source_node}.{source_attribute_name}", f"{target_node}.{target_attribute}")

    @staticmethod
    def setAttribute(object, attribute_name, value):
        cmds.setAttr(f"{object}.{attribute_name}", value)

    @staticmethod
    def setAttributeDouble3(object, attribute_name, value1, value2, value3):
        cmds.setAttr(f"{object}.{attribute_name}", value1, value2, value3, type="double3")

    #xform
    @staticmethod
    def getObjectWorldPositionMatrix(object_name) -> list:
        return cmds.xform(object_name, query =True, matrix = True, worldSpace=True)
    
    @staticmethod
    def setObjectWorldPositionMatrix(object_name, matrix):
        cmds.xform(object_name, matrix=matrix, worldSpace=True)

    @staticmethod
    def setObjectPositionMatrix(object_name, matrix):
        cmds.xform(object_name, matrix = matrix, worldSpace=False)

    #translation
    @staticmethod
    def getTranslation(object_name) -> list:
        return [MC.getAttribute(object_name, "translateX"), 
                MC.getAttribute(object_name, "translateY"), 
                MC.getAttribute(object_name, "translateZ")]

    @staticmethod
    def addTranslation(object_name, x, y, z) -> list:
        translations = MC.getTranslation(object_name)
        new_translateX = translations[0] + x
        new_translateY = translations[1] + y
        new_translateZ = translations[2] + z

        MC.setAttribute(object_name, "translateX", new_translateX)
        MC.setAttribute(object_name, "translateY", new_translateY)
        MC.setAttribute(object_name, "translateZ", new_translateZ)

        return [new_translateX, new_translateY, new_translateZ]

    @staticmethod
    def addTranslationOnAxis(object_name, amount, axis) -> list:
        new_translate = MC.getAttribute(object_name, "translate" + axis.upper()) + amount
        MC.setAttribute(object_name, "translate" + axis.upper(), new_translate)
        return 

    #joint specific methods
    @staticmethod
    def createJoint(name) -> str:
        new_joint = cmds.joint(name = name)
        MC.clearSelection()
        return new_joint
    
    @staticmethod
    def setJointRadius(joint, radius) -> None:
        cmds.setAttr(f"{joint}.radius", radius)

    @staticmethod
    def setJointPositionMatrix(name, matrix, world_space = True):
        cmds.xform(name, worldSpace=world_space, matrix = matrix)

    @staticmethod
    def resetJointOrientations(name):
        for channel in "XYZ":
            MC.setAttribute(name, "jointOrient" + channel, 0)

    @staticmethod
    def importBinaryFile(path, namespace = "import"):
        cmds.file(path, i=True, type="mayaBinary", mergeNamespacesOnClash = False, namespace=namespace)

    @staticmethod
    def selectNamespace(namespace) -> list:
        return cmds.ls(namespace + ":*")
    
    @staticmethod
    def mergeNamespaceWithRoot(namespace):
        cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)

    @staticmethod
    def applyTransform(object_name, scale = True, translate=True, rotate=True):
        cmds.makeIdentity(object_name, apply=True, scale = scale, translate=translate, rotate=rotate, normal = True)

    @staticmethod
    def applyTransformScale(object_name):
        cmds.makeIdentity(object_name, apply=True, scale = True)
    
    @staticmethod
    def applyTransformTranslate(object_name):
        cmds.makeIdentity(object_name, apply=True, translate = True)

    @staticmethod
    def applyTransformRotate(object_name):
        cmds.makeIdentity(object_name, apply=True, rotate = True)

    @staticmethod
    def scaleTransform(object_name, scale):
        cmds.scale(scale[0], scale[1], scale[2], object_name, relative =True)

    @staticmethod
    def resetTranslation(object, x = True, y= True, z = True):
        if x:
            MC.setAttribute(object, "translateX", 0)
        if y:
            MC.setAttribute(object, "translateY", 0)
        if z:
            MC.setAttribute(object, "translateZ", 0)

    @staticmethod
    def resetRotation(object, x = True, y= True, z = True):
        if x:
            MC.setAttribute(object, "rotateX", 0)
        if y:
            MC.setAttribute(object, "rotateY", 0)
        if z:
            MC.setAttribute(object, "rotateZ", 0)

    @staticmethod
    def resetScale(object, x = True, y= True, z = True):
        if x:
            MC.setAttribute(object, "scaleX", 1)
        if y:
            MC.setAttribute(object, "scaleY", 1)
        if z:
            MC.setAttribute(object, "scaleZ", 1)

    @staticmethod
    def clearTransforms(object):
        MC.resetTranslation(object)
        MC.resetRotation(object)
        MC.resetScale(object)

    #create utility nodes
    @staticmethod
    def createDecomposeNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("decomposeMatrix", name = name + "_dcm_fNode_UW")
        else:
            return cmds.createNode("decomposeMatrix", name = name + "_dcm_fNode")

    @staticmethod
    def createComposeNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("composeMatrix", name = name + "_cm_fNode_UW")
        else:
            return cmds.createNode("composeMatrix", name = name + "_cm_fNode")

    @staticmethod
    def createMultMatrixNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("multMatrix", name = name + "_mmtx_fNode_UW")
        else:
            return cmds.createNode("multMatrix", name = name + "_mmtx_fNode")

    @staticmethod      
    def createPlusMinusAverageNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("plusMinusAverage", name = name + "_pma_fNode_UW")
        else:
            return cmds.createNode("plusMinusAverage", name = name + "_pma_fNode")

    @staticmethod 
    def createRotateHelperNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("rotateHelper", name = name + "_rh_fNode_UW")
        else:
            return cmds.createNode("rotateHelper", name = name + "_rh_fNode")

    @staticmethod  
    def createBlendMatrixNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("blendMatrix", name = name + "_bMtx_fNode_UW")
        else:
            return cmds.createNode("blendMatrix", name = name + "_bMtx_fNode")

    @staticmethod 
    def createDistanceNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("distanceBetween", name = name + "_dist_fNode_UW")
        else:
            return cmds.createNode("distanceBetween", name = name + "_dist_fNode")
        
    @staticmethod
    def createMultiplyDivideNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("multiplyDivide", name = name + "_mdv_fNode_UW")
        else:
            return cmds.createNode("multiplyDivide", name = name + "_mdv_fNode")

    @staticmethod 
    def createPolyPlaneNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("polyPlane", name = name + "_polyPlane_fNode_UW")
        else:
            return cmds.createNode("polyPlane", name = name + "_polyPlane_fNode")
    
    @staticmethod
    def createMeshNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("mesh", name = name + "_meshShape_fNode_UW")
        else:
            return cmds.createNode("mesh", name = name + "_meshShape_fNode")
        
    @staticmethod
    def createPickMatrixNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("pickMatrix", name = name + "_pMtx_fNode_UW")
        else:
            return cmds.createNode("pickMatrix", name = name + "_pMtx_fNode")
        
    @staticmethod
    def createAimMatrixNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("aimMatrix", name = name + "_aimMtx_fNode_UW")
        else:
            return cmds.createNode("aimMatrix", name = name + "_aimMtx_fNode")

    #Om functions
    @staticmethod
    def force_recalculate(node_name):
        cmds.dgdirty(node_name)

    @staticmethod
    def refreshDeferred():
        cmds.evalDeferred("cmds.refresh()")