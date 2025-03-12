from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore

CLASS_DEBUG = True

class Guide_Connector():
    def __init__(self, start_guide, end_guide):
        
        self.guide = end_guide

        self._start_guide = None
        self._end_guide = None
        self._name = None

        self.start_guide = start_guide
        self.end_guide = end_guide

        self.name = self.guide.name + MNRB_Names.guide_connector_suffix

        self.initUI()
        self.initVariables()

    @property
    def start_guide(self): return self._start_guide
    @start_guide.setter
    def start_guide(self, value):
        if CLASS_DEBUG: print("%s::setting start Guide to: " % self.__class__.__name__, value)
        self._start_guide = value

    @property
    def end_guide(self): return self._end_guide
    @end_guide.setter
    def end_guide(self, value):
        if CLASS_DEBUG: print("%s::setting end Guide to: " % self.__class__.__name__, value)
        self._end_guide = value

    @property
    def name(self): return self._name
    @name.setter
    def name(self, value):
        self._name = value

    def initUI(self):
        if CLASS_DEBUG: print("%s::initUI " % self.__class__.__name__)

    def initVariables(self):
        self.nodes = []

    def build(self):
        if CLASS_DEBUG: print("%s::build " % self.__class__.__name__)
        if self.exists():
            self.remove()
        self.name = MC.createTransform(self.name)

        MC.parentObject(self.name, self.guide.node.guide_component_hierarchy)

        up_object = MC.createTransform(self.name + "_up_control")
        self.nodes.append(up_object)

        #set up_object position and parent
        MC.parentObject(up_object, self.start_guide.name)
        MC.clearTransforms(up_object)
        MC.setAttribute(up_object, "translateY", 2)

        start_decompose_node = MC.createDecomposeNode(self.start_guide.name)
        self.nodes.append(start_decompose_node)
        MC.connectAttribute(self.start_guide.name, "worldMatrix[0]", start_decompose_node, "inputMatrix")

        up_decompose_node = MC.createDecomposeNode(up_object)
        self.nodes.append(up_decompose_node)
        MC.connectAttribute(up_object, "worldMatrix[0]", up_decompose_node, "inputMatrix")

        end_decompose_node = MC.createDecomposeNode(self.end_guide.name)
        self.nodes.append(end_decompose_node)
        MC.connectAttribute(self.end_guide.name, "worldMatrix[0]", end_decompose_node, "inputMatrix")

        up_vector_subtract_node = MC.createPlusMinusAverageNode(up_object)
        self.nodes.append(up_vector_subtract_node)
        for channel in "XYZ":
            MC.connectAttribute(up_decompose_node, "outputTranslate" + channel, up_vector_subtract_node, "input3D[0].input3D" + channel.lower())
            MC.connectAttribute(start_decompose_node, "outputTranslate" + channel, up_vector_subtract_node, "input3D[1].input3D" + channel.lower())
        MC.setAttribute(up_vector_subtract_node, "operation", 2)

        up_vector_nudge_node = MC.createPlusMinusAverageNode(up_object + "_nudge")
        self.nodes.append(up_vector_nudge_node)
        MC.connectAttribute(up_vector_subtract_node, "output3D", up_vector_nudge_node, "input3D[0]")
        MC.setAttributeDouble3(up_vector_nudge_node, "input3D[1]", 0.001, 0.001, 0.001)

        aim_vector_subtract_node = MC.createPlusMinusAverageNode(self.name + "_forward")
        self.nodes.append(aim_vector_subtract_node)
        for channel in "XYZ":
            MC.connectAttribute(start_decompose_node, "outputTranslate" + channel, aim_vector_subtract_node, "input3D[0].input3D" + channel.lower())
            MC.connectAttribute(end_decompose_node, "outputTranslate" + channel, aim_vector_subtract_node, "input3D[1].input3D" + channel.lower())
        MC.setAttribute(aim_vector_subtract_node, "operation", 2)

        aim_matrix_node = MC.createAimMatrixNode(self.name + "_aimMatrix")
        self.nodes.append(aim_matrix_node)
        MC.connectAttribute(self.start_guide.name, "worldMatrix[0]", aim_matrix_node, "inputMatrix")
        MC.connectAttribute(up_object, "worldMatrix[0]", aim_matrix_node, "secondaryTargetMatrix")
        MC.connectAttribute(self.end_guide.name, "worldMatrix[0]", aim_matrix_node, "primaryTargetMatrix")
        MC.setAttribute(aim_matrix_node, "primaryInputAxisX", -1)
        MC.setAttribute(aim_matrix_node, "secondaryMode", 1)

        aim_matrix_decompose_node = MC.createDecomposeNode(self.name + "_aimMatrix")
        self.nodes.append(aim_matrix_decompose_node)
        MC.connectAttribute(aim_matrix_node, "outputMatrix", aim_matrix_decompose_node, "inputMatrix")

        position_blend_matrix_node = MC.createBlendMatrixNode(self.name + "_pos_blend")
        self.nodes.append(position_blend_matrix_node)
        MC.connectAttribute(self.start_guide.name, "worldMatrix[0]", position_blend_matrix_node, "inputMatrix")
        MC.connectAttribute(self.end_guide.name, "worldMatrix[0]", position_blend_matrix_node, "target[0].targetMatrix")
        MC.setAttribute(position_blend_matrix_node, "target[0].weight", 0.3)

        position_blend_decompose_node = MC.createDecomposeNode(self.name + "_pos_blend")
        self.nodes.append(position_blend_decompose_node)
        MC.connectAttribute(position_blend_matrix_node, "outputMatrix", position_blend_decompose_node, "inputMatrix")

        connector_guide_point_matrix_node = MC.createComposeNode(self.name + "_posMatrix")
        self.nodes.append(connector_guide_point_matrix_node)
        for channel in "XYZ":
            MC.connectAttribute(aim_matrix_decompose_node, "outputRotate" + channel, connector_guide_point_matrix_node, "inputRotate" + channel)
            MC.connectAttribute(position_blend_decompose_node, "outputTranslate" + channel, connector_guide_point_matrix_node, "inputTranslate" + channel)

        connection_distance_node = MC.createDistanceNode(self.name)
        self.nodes.append(connection_distance_node)
        MC.connectAttribute(self.start_guide.name, "worldMatrix[0]", connection_distance_node, "inMatrix1")
        MC.connectAttribute(self.end_guide.name, "worldMatrix[0]", connection_distance_node, "inMatrix2")

        adjust_distance_node = MC.createMultiplyDivideNode(self.name + "_adjustDist")
        self.nodes.append(adjust_distance_node)
        MC.connectAttribute(connection_distance_node, "distance", adjust_distance_node, "input1X")
        MC.setAttribute(adjust_distance_node, "input2X", 0.1)

        adjust_distance_negate_node = MC.createMultiplyDivideNode(self.name + "_adjustDist_Neg")
        self.nodes.append(adjust_distance_negate_node)
        MC.connectAttribute(adjust_distance_node, "outputX", adjust_distance_negate_node, "input1X")
        MC.setAttribute(adjust_distance_negate_node, "input2X", -1)

        base_connector_geometry_node = MC.createPolyPlaneNode(self.name + "_baseGeometry")
        self.nodes.append(base_connector_geometry_node)
        MC.setAttribute(base_connector_geometry_node, "width", 0.01)
        MC.setAttribute(base_connector_geometry_node, "height", 0.01)
        MC.setAttribute(base_connector_geometry_node, "subdivisionsWidth", 1)
        MC.setAttribute(base_connector_geometry_node, "subdivisionsHeight", 1)

        direction_indecies = []
        mesh_nodes = []

        for direction in [("positive", "Z"), ("positive", "Y"), ("negative", "Z"), ("negative", "Y")]:
            new_compose_node = MC.createComposeNode(self.name + "_" + direction[0] + direction[1] + "_offset")
            self.nodes.append(new_compose_node)

            if direction[0] == "positive":
                MC.connectAttribute(adjust_distance_node, "outputX", new_compose_node, "inputTranslate" + direction[1])
            else:
                MC.connectAttribute(adjust_distance_negate_node, "outputX", new_compose_node, "inputTranslate" + direction[1])

            new_multMatrix_node = MC.createMultMatrixNode(self.name + "_" + direction[0] + direction[1] + "_offset")
            self.nodes.append(new_multMatrix_node)
            MC.connectAttribute(new_compose_node, "outputMatrix", new_multMatrix_node, "matrixIn[0]")
            MC.connectAttribute(connector_guide_point_matrix_node, "outputMatrix", new_multMatrix_node, "matrixIn[1]")

            new_decompose_node = MC.createDecomposeNode(self.name + "_" + direction[0] + direction[1] + "_offset")
            self.nodes.append(new_decompose_node)
            direction_indecies.append(new_decompose_node)
            MC.connectAttribute(new_multMatrix_node, "matrixSum", new_decompose_node, "inputMatrix")

            for position in ["lower", "upper"]:
                mesh_plane_Node = MC.createMeshNode(self.name + "_" + direction[0] + direction[1] + "_" + position)
                self.nodes.append(mesh_plane_Node)
                mesh_nodes.append(mesh_plane_Node)
                mesh_plane_node_parent = MC.getObjectParentNode(mesh_plane_Node)[0]
                MC.parentShape(mesh_plane_Node, self.name)
                MC.deleteNode(mesh_plane_node_parent)
                MC.connectAttribute(base_connector_geometry_node, "output", mesh_plane_Node, "inMesh")
                MC.connectAttribute(new_decompose_node, "outputTranslate", mesh_plane_Node, "pnts[0]")

        
        for index in range(len(direction_indecies)):
            target_01_index = index + (index - 1) + 3
            if target_01_index > (len(mesh_nodes) - 1):
                target_01_index = 0
            target_02_index = target_01_index + 1

            if CLASS_DEBUG: 
                print("%s::Trying to Connect: " % self.__class__.__name__)
                print("%s:: \t\t\t indecies: " % self.__class__.__name__, "source index: ", index, " target_01_index: ", target_01_index, " target_02_index", target_02_index)
                print("%s:: \t\t\t " % self.__class__.__name__, direction_indecies[index], "to", mesh_nodes[target_01_index], "point 1")
                print("%s:: \t\t\t " % self.__class__.__name__, start_decompose_node, "to", mesh_nodes[target_01_index], "point 2")
                print("%s:: \t\t\t " % self.__class__.__name__, start_decompose_node, "to", mesh_nodes[target_01_index], "point 3")
                print("%s:: \t\t\t " % self.__class__.__name__, direction_indecies[index], "to", mesh_nodes[target_02_index], "point 1")
                print("%s:: \t\t\t " % self.__class__.__name__, end_decompose_node, "to", mesh_nodes[target_02_index], "point 2")
                print("%s:: \t\t\t " % self.__class__.__name__, end_decompose_node, "to", mesh_nodes[target_02_index], "point 3")

            MC.connectAttribute(direction_indecies[index], "outputTranslate", mesh_nodes[target_01_index], "pnts[1]")
            MC.connectAttribute(start_decompose_node, "outputTranslate", mesh_nodes[target_01_index], "pnts[2]")
            MC.connectAttribute(start_decompose_node, "outputTranslate", mesh_nodes[target_01_index], "pnts[3]")
            MC.connectAttribute(direction_indecies[index], "outputTranslate", mesh_nodes[target_02_index], "pnts[1]")
            MC.connectAttribute(end_decompose_node, "outputTranslate", mesh_nodes[target_02_index], "pnts[2]")
            MC.connectAttribute(end_decompose_node, "outputTranslate", mesh_nodes[target_02_index], "pnts[3]")

        MC.refreshDeferred()
        MC.force_recalculate(aim_matrix_node)


    def remove(self):
        if CLASS_DEBUG: print("%s::remove " % self.__class__.__name__)
        if self.exists():
            MC.deleteNode(self.name)
            while(self.nodes != []):
                if MC.objectExists(self.nodes[-1]):
                    MC.deleteNode(self.nodes[-1])
                    self.nodes.pop()
                else:
                    self.nodes.pop()

    def updateColor(self):
        if CLASS_DEBUG: print("%s::updateColor " % self.__class__.__name__)
    
    def update(self):
        if CLASS_DEBUG: print("%s::update " % self.__class__.__name__)
    
    def exists(self):
        if MC.objectExists(self.name): return True
        else: return False