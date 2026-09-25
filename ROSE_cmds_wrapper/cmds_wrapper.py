import os
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
    def unparentObject(child):
        cmds.parent(child, world=True)
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
    def createSpaceLocator(position) -> str: #type: ignore
        new_space_locator = cmds.spaceLocator(p=position)
        MC.clearSelection()
        return new_space_locator[0]
    
    @staticmethod
    def createSpaceLocator(position, name) -> str: #type: ignore
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

# Nurbs methods
    @staticmethod
    def createNurbsSphere(name) -> str:
        new_sphere = cmds.sphere(name = name)[0]
        MC.clearSelection()
        return new_sphere
    
    @staticmethod
    def createNurbsCone(name, axis, radius) -> str:
        new_cone = cmds.cone(name = name, axis = axis, radius = radius)[0]
        MC.clearSelection()
        return new_cone

    @staticmethod
    def setNurbsSphereShapeRadius(object, size) -> None:
        shape_node = MC.listSourceConnections(object, "create")[0]
        cmds.setAttr(f"{shape_node}.radius", size)

    @staticmethod
    def setNurbsSphereShapeDegree(object, degree) -> None:
        shape_node = MC.listSourceConnections(object, "create")[0]
        cmds.setAttr(f"{shape_node}.degree", degree)

    @staticmethod
    def setNurbsSphereShapeSpans(object, spans) -> None:
        shape_node = MC.listSourceConnections(object, "create")[0]
        cmds.setAttr(f"{shape_node}.spans", spans)

    @staticmethod
    def setNurbsSphereShapeSections(object, sections) -> None:
        shape_node = MC.listSourceConnections(object, "create")[0]
        cmds.setAttr(f"{shape_node}.sections", sections)

    @staticmethod
    def createNurbsCircle(name, x_normal = 0, y_normal = 1, z_normal = 0):
        new_circle = cmds.circle(name = name, normalX = 0, normalY = 1, normalZ = 0)
        MC.clearSelection()
        return new_circle[0]
    
# lambert methods
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

# Attribute Functions
    @staticmethod
    def addStringAttribute(node_name, target_attribute, value, is_hidden) -> None:
        cmds.addAttr(node_name, dataType="string", longName = target_attribute, hidden = is_hidden)
        cmds.setAttr(f"{node_name}.{target_attribute}", value, type="string")

    @staticmethod
    def addFloatAttribute(node_name, attribute_name, default_value = 0, min = None, max = None, keyable = True):
        limits = {}
        if min is not None: limits["minValue"] = min
        if max is not None: limits["maxValue"] = max
        cmds.addAttr(node_name, longName=attribute_name, attributeType="float",
                     defaultValue=default_value, keyable=keyable, **limits)
        if not keyable:
            cmds.setAttr(f"{node_name}.{attribute_name}", cb = True)

    @staticmethod
    def addBoolAttribute(node_name, attribute_name, default_state = False, keyable = True):
        cmds.addAttr(node_name, attributeType="bool", ln=attribute_name, defaultValue = default_state, keyable=keyable)
        if keyable == False:
            cmds.setAttr(f"{node_name}.{attribute_name}", cb = True)

    @staticmethod
    def addIntAttribute(node_name, attribute_name, default_value = 0, min = None, max = None, keyable = True):
        limits = {}
        if min is not None: limits["minValue"] = min
        if max is not None: limits["maxValue"] = max
        cmds.addAttr(node_name, longName=attribute_name, attributeType="long",
                     defaultValue=default_value, keyable=keyable, **limits)
        if not keyable:
            cmds.setAttr(f"{node_name}.{attribute_name}", cb = True)

    @staticmethod
    def addEnumAttribute(node_name, attribute_name, option_names, default_index = 0, keyable = True):
        #Maya takes the options as one colon-separated string
        cmds.addAttr(node_name, longName=attribute_name, attributeType="enum",
                     enumName=":".join(option_names), defaultValue=default_index, keyable=keyable)
        if not keyable:
            cmds.setAttr(f"{node_name}.{attribute_name}", cb = True)

    @staticmethod
    def addProxyAttribute(node_name, attribute_name, source_node, source_attribute) -> None:
        """Add an attribute that *is* another node's attribute, not a copy of it.

        This is how the Attribute Editor puts a component's attribute onto a
        control: editing either side changes the same value. Only works for the
        proxyable types (bool/int/float/enum/angle/distance/time) - a string,
        matrix or message attribute has to be connected instead.
        """
        cmds.addAttr(node_name, longName=attribute_name, proxy="%s.%s" % (source_node, source_attribute))

    @staticmethod
    def deleteAttribute(node_name, attribute_name) -> None:
        cmds.deleteAttr("%s.%s" % (node_name, attribute_name))

    @staticmethod
    def attributeExists(node_name, attribute_name) -> bool:
        return cmds.attributeQuery(attribute_name, node=node_name, exists=True)

    @staticmethod
    def getAttributeDefault(node_name, attribute_name):
        defaults = cmds.attributeQuery(attribute_name, node=node_name, listDefault=True) or []
        if not defaults:
            return None
        value = defaults[0]
        #Maya reports every default as a float; hand it back in the type the
        #definition holds, so comparisons are like for like
        attribute_type = cmds.getAttr("%s.%s" % (node_name, attribute_name), type=True)
        if attribute_type == "bool":
            return bool(value)
        if attribute_type in ("long", "short", "byte") or cmds.attributeQuery(attribute_name, node=node_name, listEnum=True):
            return int(value)
        return value

    @staticmethod
    def getAttributeMinimum(node_name, attribute_name):
        #None means "no minimum set", which is different from a minimum of 0
        if not cmds.attributeQuery(attribute_name, node=node_name, minExists=True):
            return None
        values = cmds.attributeQuery(attribute_name, node=node_name, minimum=True) or []
        return values[0] if values else None

    @staticmethod
    def getAttributeMaximum(node_name, attribute_name):
        if not cmds.attributeQuery(attribute_name, node=node_name, maxExists=True):
            return None
        values = cmds.attributeQuery(attribute_name, node=node_name, maximum=True) or []
        return values[0] if values else None

    @staticmethod
    def getAttributeEnumOptions(node_name, attribute_name) -> list:
        #Maya hands the options back as one colon-separated string inside a list
        enum_strings = cmds.attributeQuery(attribute_name, node=node_name, listEnum=True) or []
        if not enum_strings:
            return []
        return [option for option in enum_strings[0].split(":") if option]

    @staticmethod
    def listUserDefinedAttributes(node_name) -> list:
        #only attributes added by us/the user, never Maya's own - returns [] rather
        #than None when a node has none, which cmds.listAttr does not
        return cmds.listAttr(node_name, userDefined=True) or []

    @staticmethod
    def setAttributeKeyable(node_name, attribute_name, keyable = True) -> None:
        cmds.setAttr(f"{node_name}.{attribute_name}", keyable=keyable)
        if not keyable:
            #non-keyable but still visible in the channel box, matching how the
            #component visibility attributes are set up
            cmds.setAttr(f"{node_name}.{attribute_name}", cb = True)

    @staticmethod
    def getAttribute(node_name, attribute_name):
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
    def setMatrixAttribute(object, attribute_name, matrix) -> None:
        #a matrix set whole, rather than decomposed into translate/rotate/scale and
        #recomposed: that round trip silently drops shear and forces a rotate order
        cmds.setAttr(f"{object}.{attribute_name}", list(matrix), type="matrix")

    @staticmethod
    def getJointOrient(object):
        #None for anything that isn't a joint - only joints carry this, and it is
        #applied on top of rotate, so a matrix constraint has to cancel it
        if not cmds.attributeQuery("jointOrient", node=object, exists=True):
            return None
        return cmds.getAttr(f"{object}.jointOrient")[0]

    @staticmethod
    def getObjectLocalMatrix(object) -> list:
        return cmds.getAttr(f"{object}.matrix")

    @staticmethod
    def getObjectParentWorldMatrix(object) -> list:
        #identity when the object sits at the world root, so callers can always
        #treat the result as a matrix to divide out
        parent = MC.getObjectParentNode(object)
        if not parent:
            return [1.0, 0.0, 0.0, 0.0,
                    0.0, 1.0, 0.0, 0.0,
                    0.0, 0.0, 1.0, 0.0,
                    0.0, 0.0, 0.0, 1.0]
        return cmds.xform(parent[0], query=True, matrix=True, worldSpace=True)

    @staticmethod
    def setAttributeDouble3(object, attribute_name, value1, value2, value3):
        cmds.setAttr(f"{object}.{attribute_name}", value1, value2, value3, type="double3")

    @staticmethod
    def lockAndHideAllAttributes(node_name):
        for axis in "XYZ":
            cmds.setAttr(f"{node_name}.translate{axis}", keyable=False, cb=False)
            cmds.setAttr(f"{node_name}.rotate{axis}", keyable=False, cb=False)
            cmds.setAttr(f"{node_name}.scale{axis}", keyable=False, cb=False)
        cmds.setAttr(f"{node_name}.visibility", keyable=False, cb=False)


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

# joint specific methods
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

# IK Functions
    @staticmethod
    def createRotatePlaneIkSolver(name, joint_chain) -> list[str]:
        ik_objects = cmds.ikHandle(
            name=name + "rps_ikHandle",
            startJoint=joint_chain[0],
            endEffector=joint_chain[-1],
            solver="ikRPsolver")
        MC.renameObject("effector1", name + "rps_effector")
        return ik_objects

    @staticmethod
    def createPoleVectorConstraint(source, target_Ik_handle) -> str: # type: ignore
        pole_vector_constraint = cmds.poleVectorConstraint(source, target_Ik_handle)
        return pole_vector_constraint

    @staticmethod
    def createPoleVectorConstraint(source, target_Ik_handle, name) -> str:
        pole_vector_constraint = cmds.poleVectorConstraint(source, target_Ik_handle, name=name)
        return pole_vector_constraint

# Maya Constraints
    @staticmethod
    def createOrientConstraint(source_object, target_object, maintain_offset = True) -> str:
        return cmds.orientConstraint(source_object, target_object, maintainOffset = maintain_offset)[0]

    @staticmethod
    def createPointConstraint(driver, driven, maintain_offset = True) -> str:
        return cmds.pointConstraint(driver, driven, maintainOffset = maintain_offset)[0]

    @staticmethod
    def createScaleConstraint(driver, driven, maintain_offset = True) -> str:
        return cmds.scaleConstraint(driver, driven, maintainOffset = maintain_offset)[0]

    @staticmethod
    def createAimConstraint(driver, driven, maintain_offset = True) -> str:
        return cmds.aimConstraint(driver, driven, maintainOffset = maintain_offset)[0]

    @staticmethod
    def createParentConstraint(driver, driven, maintain_offset = True) -> str:
        return cmds.parentConstraint(driver, driven, maintainOffset=maintain_offset)[0]

# Math nodes
#
#Maya's newer single-purpose math nodes. They read far better in a graph than
#multiplyDivide/plusMinusAverage doing everything, and they carry angle units
#properly, which matters when trigonometry is involved.

    @staticmethod
    def createAtan2Node(name) -> str:
        return cmds.createNode("atan2", name = name + "_atan2_fNode")

    @staticmethod
    def createCosNode(name) -> str:
        return cmds.createNode("cos", name = name + "_cos_fNode")

    @staticmethod
    def createMathMultiplyNode(name) -> str:
        return cmds.createNode("multiply", name = name + "_mult_fNode")

    @staticmethod
    def createSumNode(name) -> str:
        return cmds.createNode("sum", name = name + "_sum_fNode")

    @staticmethod
    def createSubtractNode(name) -> str:
        return cmds.createNode("subtract", name = name + "_sub_fNode")

    @staticmethod
    def createDivideNode(name) -> str:
        return cmds.createNode("divide", name = name + "_div_fNode")

    @staticmethod
    def createPowerNode(name) -> str:
        return cmds.createNode("power", name = name + "_pow_fNode")

# Transform limits

    @staticmethod
    def setRotationLimit(object_name, axis, minimum = None, maximum = None) -> None:
        """Clamp one rotation axis. None leaves that end unlimited.

        Limits are attributes (`minRotZLimit` / `maxRotZLimit`), so the value can
        be connected afterwards and driven live - see getRotationLimitAttribute.
        """
        axis = axis.upper()

        #Maya takes both ends of an axis together, as (min, max) pairs - and the
        #flags are enableRotationZ / rotationZ, not the ...Limit spelling the
        #attribute names use
        enable_minimum = minimum is not None
        enable_maximum = maximum is not None

        cmds.transformLimits(object_name, **{
            "enableRotation%s" % axis: (enable_minimum, enable_maximum),
            "rotation%s" % axis: (minimum if enable_minimum else -360.0,
                                  maximum if enable_maximum else 360.0),
        })

    @staticmethod
    def getRotationLimitAttribute(axis, is_maximum) -> str:
        """The attribute name holding a rotation limit, for connecting to."""
        return "%sRot%sLimit" % ("max" if is_maximum else "min", axis.upper())

    @staticmethod
    def getRotationLimits(object_name, axis) -> list:
        axis = axis.upper()
        enabled = cmds.transformLimits(object_name, query=True, **{"enableRotation%s" % axis: True})
        values = cmds.transformLimits(object_name, query=True, **{"rotation%s" % axis: True})
        return [enabled, values]

# Expressions

    @staticmethod
    def createExpression(name, expression_string, attached_object = None) -> str:
        """Create a Maya expression node.

        Left unattached by default. An expression created with `object=` is
        deleted along with that object, which sounds convenient but hides the
        node's lifetime from the component that made it - the same trap the
        matrix constraint networks had, where DG nodes survived deleting the
        transform hierarchy and quietly accumulated. A component should track
        what it creates and clear it on rebuild instead.
        """
        keyword_arguments = {
            "string": expression_string,
            "name": name,
            #the expression reads world positions with xform, which the DG does
            #not see as inputs, so it has to be told to run every frame
            "alwaysEvaluate": True,
            "unitConversion": "all",
        }

        if attached_object is not None:
            keyword_arguments["object"] = attached_object

        return cmds.expression(**keyword_arguments)

    @staticmethod
    def setExpressionString(expression_node, expression_string) -> None:
        cmds.expression(expression_node, edit=True, string=expression_string)

    @staticmethod
    def getExpressionString(expression_node) -> str:
        return cmds.expression(expression_node, query=True, string=True)

    @staticmethod
    def createLocator(name) -> str:
        return cmds.spaceLocator(name=name)[0]

    @staticmethod
    def createAimConstraintWithUpObject(driver, driven, up_object,
                                        aim_vector = (1, 0, 0), up_vector = (0, 1, 0),
                                        maintain_offset = False) -> str:
        """Aim `driven` at `driver`, with a specific object defining up.

        The plain aimConstraint wrapper uses Maya's default world up, which flips
        as soon as the aim direction lines up with it. An explicit up object that
        travels with the rig removes that.
        """
        return cmds.aimConstraint(driver, driven,
                                  maintainOffset = maintain_offset,
                                  aimVector = aim_vector,
                                  upVector = up_vector,
                                  worldUpType = "object",
                                  worldUpObject = up_object)[0]

# Plugin Functions

    @staticmethod
    def isPluginLoaded(plugin_name) -> bool:
        try:
            return bool(cmds.pluginInfo(plugin_name, query = True, loaded = True))
        except Exception:
            return False

    @staticmethod
    def loadPluginIfAvailable(plugin_name) -> bool:
        if MC.isPluginLoaded(plugin_name):
            return True
        try:
            cmds.loadPlugin(plugin_name, quiet = True)
            return MC.isPluginLoaded(plugin_name)
        except Exception:
            return False

    @staticmethod
    def getPluginNodeTypeMap() -> dict:
        """node type -> the plugin providing it, for every loaded plugin."""
        provided = {}

        for plugin_name in cmds.pluginInfo(query = True, listPlugins = True) or []:
            try:
                node_types = cmds.pluginInfo(plugin_name, query = True, dependNode = True) or []
            except Exception:
                node_types = []

            for node_type in node_types:
                provided[node_type] = plugin_name

        return provided

    @staticmethod
    def getRequiredPluginsForNodes(nodes) -> list:
        """Which plugins these nodes need in order to evaluate.

        Determined by inspecting the node types actually present rather than by
        what a component declared it might build - a component can declare a
        plugin and then not use it on a given rig, and only what ends up in the
        exported hierarchy matters to whoever opens it.
        """
        provided = MC.getPluginNodeTypeMap()
        required = set()

        for node in nodes or []:
            try:
                node_type = cmds.nodeType(node)
            except Exception:
                continue
            if node_type in provided:
                required.add(provided[node_type])

        return sorted(required)

# Maya Org Functios
    @staticmethod
    def importBinaryFile(path, namespace = "import"):
        cmds.file(path, i=True, type="mayaBinary", mergeNamespacesOnClash = False, namespace=namespace)

    @staticmethod
    def exportSceneAs(file_path) -> None:
        #exportAll writes a copy without changing the current scene's own file
        #association - a package/ship action should never rename the artist's
        #actual working file out from under them
        cmds.file(file_path, exportAll=True, type="mayaBinary", force=True)

    @staticmethod
    def exportSelectedAs(file_path) -> None:
        cmds.file(file_path, exportSelected=True, type="mayaBinary", force=True)

    @staticmethod
    def selectNamespace(namespace) -> list:
        return cmds.ls(namespace + ":*")
    
    @staticmethod
    def mergeNamespaceWithRoot(namespace):
        cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)

# Transform Functions
    @staticmethod
    def getTranslation(object_name) -> list:
        return [MC.getAttribute(object_name, "translateX"), 
                MC.getAttribute(object_name, "translateY"), 
                MC.getAttribute(object_name, "translateZ")]

    @staticmethod
    def setTranslation(object_name, translation_x, translation_y, translation_z) -> None:
        cmds.setAttr(f"{object_name}.translate", translation_x, translation_y, translation_z)

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
    def addTranslationOnAxis(object_name, amount, axis):
        new_translate = MC.getAttribute(object_name, "translate" + axis.upper()) + amount
        MC.setAttribute(object_name, "translate" + axis.upper(), new_translate)

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

# Create utility nodes
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
    def createReverseNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("reverse", name = name + "_rev_fNode_UW")
        else:
            return cmds.createNode("reverse", name = name + "_rev_fNode")

    @staticmethod
    def createConditionNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("condition", name = name + "_cond_fNode_UW")
        else:
            return cmds.createNode("condition", name = name + "_cond_fNode")

    @staticmethod
    def createClampNode(name, underworld = False) -> str:
        if underworld:
            return cmds.createNode("clamp", name = name + "_clamp_fNode_UW")
        else:
            return cmds.createNode("clamp", name = name + "_clamp_fNode")

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

# Skinning Functions
    @staticmethod
    def getViewportSelection() -> list:
        return cmds.ls(sl=True)

    @staticmethod
    def objectIsMesh(name) -> bool:
        if cmds.objectType(name) == "mesh":
            return True
        shapes = cmds.listRelatives(name, shapes=True, type="mesh") or []
        return len(shapes) > 0

    @staticmethod
    def createSkinCluster(joint_names, mesh_name, cluster_name, bind_method = 0, skin_method = 0,
                           normalize_weights = 1, weight_distribution = 0, maximum_influences = 5,
                           obey_maximum_influences = True, allow_multiple_bind_poses = True) -> str:
        #bind_method: 0=Closest Distance, 1=Closest in Hierarchy, 2=Heat Map, 3=Geodesic Voxel
        #skin_method: 0=Classic Linear, 1=Dual Quaternion, 2=Weight Blended
        #normalize_weights: 0=None, 1=Interactive, 2=Post
        #weight_distribution: 0=Distance, 1=Neighbors
        #allow_multiple_bind_poses is intentionally NOT passed through - confirmed
        #wrong as multipleBindPose (TypeError: Invalid flag). Get the real flag by
        #using Maya's Bind Skin option box with that checkbox toggled and reading
        #the skinCluster command Maya echoes to the Script Editor, then it can be
        #wired back in here
        skin_cluster = cmds.skinCluster(
            *joint_names, mesh_name, name=cluster_name, toSelectedBones=True,
            bindMethod=bind_method, skinMethod=skin_method, normalizeWeights=normalize_weights,
            weightDistribution=weight_distribution, maximumInfluences=maximum_influences,
            obeyMaxInfluences=obey_maximum_influences
        )
        MC.clearSelection()
        return skin_cluster[0]

    #exact deformerWeights flags to be verified/adjusted against the target Maya
    #version's documentation once this is exercised for real
    @staticmethod
    def exportDeformerWeights(deformer_name, mesh_name, file_path) -> None:
        directory, file_name = os.path.split(file_path)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        cmds.select(mesh_name)
        cmds.deformerWeights(file_name, path=directory, deformer=deformer_name, export=True)
        MC.clearSelection()

    @staticmethod
    def importDeformerWeights(deformer_name, mesh_name, file_path) -> None:
        directory, file_name = os.path.split(file_path)
        cmds.select(mesh_name)
        cmds.deformerWeights(file_name, path=directory, deformer=deformer_name, im=True, method="index")
        MC.clearSelection()

# Om functions
    @staticmethod
    def force_recalculate(node_name):
        cmds.dgdirty(node_name)

    @staticmethod
    def refreshDeferred():
        cmds.evalDeferred("cmds.refresh()")