"""Space switching for a control fed by a multi-connection input socket.

Built entirely at componentBuild, so a component is complete before it is ever
connected: one input transform per space wired into the socket, all placed where
the control sits; a blendMatrix choosing between them by an enum on the control;
and a result transform the control follows. connectComponent then only attaches
each input to its space, keeping the offset - which is what puts every space
exactly on the control's rest place, and why the blend needs no offsets of its
own. An input whose space is later disconnected is still there to hook up to
anything.

With nothing connected there is one input, which follows whatever default space
the component hands connect() - usually its own parent.
"""

from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_Constraints.constraint_types import ConstraintType #type: ignore
from MNRB.ROSE_naming.ROSE_names import ROSE_Names #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")


class SpaceSwitch:

    def __init__(self, node, name, input_index, switch_control, attribute_name = "space"):
        """name: the base of every node this makes - <name><i>_srtIn inputs,
        <name>_srt result, <name>Switch blend. switch_control: the control
        object that gets the enum."""
        self.node = node
        self.name = name
        self.input_index = input_index
        self.control = switch_control
        self.attribute_name = attribute_name

        #the spaces as they were connected at build time - the inputs and the enum
        #were made from these
        self.spaces = []
        self.inputs = []
        self.result = None

    def getConnectedSpaces(self):
        """Every component output wired into the socket, in connection order,
        without the output suffix."""
        #asked first: getAllInputConnectionValuesAt reports an unconnected
        #socket as an error, and a space input is optional
        if not self.node.isInputSocketConnected(self.input_index):
            return []

        spaces = self.node.getAllInputConnectionValuesAt(self.input_index) or []
        #the same output wired in twice would only be a duplicate enum entry
        return list(dict.fromkeys(spaces))

# componentBuild

    def build(self, position):
        """Make the inputs, the switch and the result transform. Returns the
        result, for the control to follow."""
        prefix = self.node.getComponentFullPrefix()

        #read from the graph, not from Maya: the edges exist before anything
        #upstream is built, which is what lets this happen at componentBuild
        self.spaces = self.getConnectedSpaces()
        self.inputs = [self.createInput(index, position)
                       for index in range(max(1, len(self.spaces)))]

        self.result = MC.createTransform(prefix + self.name + "_srt")
        MC.parentObject(self.result, self.node.system_hierarchy)
        MC.setObjectWorldPositionMatrix(self.result, position)
        MC.applyTransformScale(self.result)

        if len(self.inputs) == 1:
            #nothing to switch between
            self.node.constrain(self.result, self.inputs[0],
                                maintain_offset = False, constraint_type = ConstraintType.MATRIX)
        else:
            self.buildSwitch()

        return self.result

    def createInput(self, index, position):
        space_input = MC.createTransform(
            self.node.getComponentFullPrefix() + "%s%d" % (self.name, index) + ROSE_Names.input_suffix)
        MC.parentObject(space_input, self.node.input_hierarchy)
        MC.setObjectWorldPositionMatrix(space_input, position)
        MC.applyTransformScale(space_input)
        return space_input

    def buildSwitch(self):
        """The first input is the blend's base, every other one a target whose
        weight is 1 only while the enum selects it, so the output is always
        exactly one space, never a mix. The result is brought into the result
        transform's parent space and driven into its offsetParentMatrix, the same
        way a matrix parent constraint does it."""
        prefix = self.node.getComponentFullPrefix()
        control_name = self.control.name

        MC.addEnumAttribute(control_name, self.attribute_name,
                            [self.getSpaceLabel(space) for space in self.spaces])

        blend = self.node.trackBuiltNode(MC.createBlendMatrixNode(prefix + self.name + "Switch"))

        for index, space_input in enumerate(self.inputs):
            if index == 0:
                MC.connectAttribute(space_input, "worldMatrix[0]", blend, "inputMatrix")
                continue

            target = "target[%d]" % (index - 1)
            MC.connectAttribute(space_input, "worldMatrix[0]", blend, target + ".targetMatrix")

            #1 while the enum sits on this space, 0 otherwise
            is_active = self.node.trackBuiltNode(
                MC.createConditionNode(prefix + "%s%dActive" % (self.name, index)))
            MC.connectAttribute(control_name, self.attribute_name, is_active, "firstTerm")
            MC.setAttribute(is_active, "secondTerm", index)
            MC.setAttribute(is_active, "operation", 0)            # equal
            MC.setAttribute(is_active, "colorIfTrueR", 1.0)
            MC.setAttribute(is_active, "colorIfFalseR", 0.0)
            MC.connectAttribute(is_active, "outColorR", blend, target + ".weight")

        #world -> the result's parent space. The DAG parent's inverse, not its own
        #parentInverseMatrix, which since Maya 2020 includes the offsetParentMatrix
        #this drives - see constraint.connectChildParentInverse
        local_matrix = self.node.trackBuiltNode(MC.createMultMatrixNode(prefix + self.name + "Local"))
        MC.connectAttribute(blend, "outputMatrix", local_matrix, "matrixIn[0]")
        MC.connectAttribute(self.node.system_hierarchy, "worldInverseMatrix[0]", local_matrix, "matrixIn[1]")

        MC.connectAttribute(local_matrix, "matrixSum", self.result, "offsetParentMatrix", force = True)
        MC.clearTransforms(self.result)

    def getSpaceLabel(self, space):
        #":" separates enum entries and "=" sets an entry's index, so neither may
        #appear in a label
        return space.replace(":", "_").replace("=", "_")

# connectComponent

    def connect(self, default_space):
        """Attach each input to its space, keeping the offset it was built with.

        default_space: the full name of the transform to follow when nothing is
        connected at all - usually the component's own parent output."""
        connected_spaces = self.getConnectedSpaces()

        #the inputs and the enum were made from the edges at componentBuild
        if connected_spaces != self.spaces:
            log.warning("%s:: --SpaceSwitch.connect:: the '%s' connections changed since the "
                        "component was built - rebuild it to update the space switch"
                        % (self.node.__class__.__name__, self.name))

        if not connected_spaces:
            #no space at all: every input rides with the default
            for space_input in self.inputs:
                self.node.constrain(space_input, default_space)
            return

        #an input past the connected ones is left unattached, free to be hooked up
        for space_input, space in zip(self.inputs, connected_spaces):
            self.node.constrain(space_input, space + ROSE_Names.output_suffix)
