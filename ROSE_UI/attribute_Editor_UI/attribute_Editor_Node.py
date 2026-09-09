from PySide6.QtWidgets import QLabel #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_NodeProperties import NodeEditorNodeProperties #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_Socket import LEFT #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_GraphicNode import AttributeEditor_QGraphicNode #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_categories import CATEGORY_OPERATOR #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

class AttributeNodeProperties(NodeEditorNodeProperties):
    def __init__(self, node):
        super().__init__(node)
        #nothing in this graph has the rig canvas's name/uniqueness rules, so a
        #node is valid until something specific invalidates it (see validate())
        self.is_valid = True

    def initUI(self):
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.layout.addWidget(self.description_label)

    def refresh(self):
        self.description_label.setText(self.node.getDescription())

    def serialize(self):
        return super().serialize()

    def deserialize(self, data, hashmap = {}, restore_id = True):
        return super().deserialize(data, hashmap, restore_id)


class AttributeGraphNode(NodeEditorNode):
    """Base for every node on the attribute canvas.

    The graph expresses two different things with one edge type, distinguished by
    what the edge lands on: an edge into a *control* means "proxy this attribute
    onto that control", an edge into an *attribute* means "drive that attribute
    from this one". Operators sit in between and become Maya utility nodes.
    """

    operation_code = -1
    operation_title = "AttributeNode"
    icon = ""
    category = CATEGORY_OPERATOR

    Graphics_Node_Class = AttributeEditor_QGraphicNode
    Node_Properties_Class = AttributeNodeProperties
    #no per-socket labels: a node here has at most one input and one output, and
    #its title already names the attribute or control. Keeps the nodes compact and
    #avoids the content widget entirely.
    Node_Content_Class = None

    def __init__(self, scene, inputs = None, outputs = None):
        inputs = inputs if inputs is not None else [["in", SocketTypes.attribute, False]]
        outputs = outputs if outputs is not None else [["out", SocketTypes.attribute, True]]

        super().__init__(scene, self.__class__.operation_title, inputs, outputs)

        #the Maya node/plug this produced on the last build, so a rebuild can
        #clean up after itself rather than leaving orphaned utility nodes
        self.built_maya_nodes = []

    def getDescription(self):
        return self.__class__.operation_title

    def getSubtitle(self):
        """The owning component, drawn under the title. Two components' identically
        named attributes are otherwise indistinguishable on the canvas."""
        return ""

    def getSocketPosition(self, index, position):
        #inputs stack down the left, outputs down the right, each counted on its
        #own side. The inherited version runs one index sequence across both, which
        #puts a two-input/one-output node's sockets at three different heights.
        graphic_node = self.grNode
        is_input = position == LEFT
        side_index = index if is_input else index - len(self.inputs)

        x = 0 if is_input else graphic_node.width
        y = (graphic_node.title_height + graphic_node._subtitle_height
             + graphic_node.getSocketRowHeight() * side_index + graphic_node.socket_padding)
        return [x, y]

# Graph traversal

    def getUpstreamNode(self, socket_index = 0):
        if socket_index >= len(self.inputs):
            return None
        socket = self.inputs[socket_index]
        if not socket.edges:
            return None
        return socket.edges[0].getOtherSocket(socket).node

    def getUpstreamNodes(self, socket_index = 0):
        if socket_index >= len(self.inputs):
            return []
        socket = self.inputs[socket_index]
        return [edge.getOtherSocket(socket).node for edge in socket.edges]

    def getDownstreamNodes(self, socket_index = 0):
        if socket_index >= len(self.outputs):
            return []
        socket = self.outputs[socket_index]
        return [edge.getOtherSocket(socket).node for edge in socket.edges]

    def isDriven(self):
        """True when something upstream feeds this node - i.e. its value is owned
        by an incoming connection rather than being freely editable."""
        return self.getUpstreamNode(0) is not None

# Build contract

    def getOutputPlug(self):
        """The '<maya node>.<attribute>' this node's value can be read from, or
        None if it has nothing to offer. Overridden by every concrete node."""
        return None

    def buildNode(self):
        """Create whatever Maya nodes this node represents. Runs before any
        connections are made, so every getOutputPlug() is resolvable by then."""
        return True, ""

    def removeBuiltNodes(self):
        from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
        for maya_node in self.built_maya_nodes:
            if MC.objectExists(maya_node):
                MC.deleteNode(maya_node)
        self.built_maya_nodes = []

    def isDeprecated(self):
        """True when what this node points at no longer exists in the rig.

        Distinct from merely invalid: an invalid node is wired wrongly and the
        user can fix it, a deprecated one has lost its source and is what
        'Remove Deprecated' clears out.
        """
        return False

    def setValidity(self, is_valid):
        self.properties.is_valid = is_valid
        self.properties.refresh()
        #paint() reads is_valid and isDeprecated(), so the node has to be told to
        #redraw - nothing else triggers it when validity changes off the back of
        #an edge or a rig change
        if self.grNode is not None:
            self.grNode.update()
        return is_valid

    def validate(self):
        """Recomputed after every graph change - see AttributeEditorScene."""
        return self.setValidity(True)

    def serialize(self):
        result_data = super().serialize()
        result_data['operation_code'] = self.__class__.operation_code
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        return super().deserialize(data, hashmap, restore_id, exists)
