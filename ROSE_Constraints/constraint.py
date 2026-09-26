import hashlib
import maya.api.OpenMaya as om #type: ignore
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_cmds_wrapper.matrix_functions import Matrix_functions #type: ignore
from MNRB.ROSE_naming.ROSE_names import ROSE_Names #type: ignore
from MNRB.ROSE_Constraints.constraint_types import (ConstraintType, ConstraintKind, enumValue, #type: ignore
                                                    ConstraintChannels,
                                                    mapNameToConstraintType, mapNameToConstraintKind)
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

#which channels each kind drives, so matrix and native modes agree on what a kind
#means rather than each having its own idea.
#
#Keyed by enum *value*, not by the member: a member arriving from a module that
#the shelf reloaded at a different time belongs to a different class object and
#would miss the lookup entirely. Same reason every comparison below goes through
#enumValue - see constraint_types.enumValue.
KIND_CHANNELS = {
    ConstraintKind.PARENT.value: (True, True, False),
    ConstraintKind.POINT.value:  (True, False, False),
    ConstraintKind.ORIENT.value: (False, True, False),
    ConstraintKind.SCALE.value:  (False, False, True),
    ConstraintKind.AIM.value:    (False, True, False),
}

class constraint(Serializable):
    """One driver-to-driven relationship, built either way.

    The point of the class is that a component says *what* it wants constrained
    and never *how*: the component's constraint_type property decides, and a call
    site can override it for one specific constraint by passing constraint_type
    directly - deliberately code-only, since which technique one inner control
    uses is a rigging decision, not a user preference.

    Not serialized. These are created during a build, not authored, so they are
    rebuilt from the component's own code every time.
    """

    def __init__(self, node, child, parent, kind = ConstraintKind.PARENT,
                 constraint_type = None, maintain_offset = True, channels = None):
        super().__init__()

        self.node = node
        self.child = child
        self.parent = parent
        #remapped rather than stored as handed over: a shelf Reload rebuilds the
        #enum classes, and a caller that was reloaded at a different time holds
        #members of the older class object which match nothing here
        self.kind = mapNameToConstraintKind(kind)

        #None means "whatever the component is set to"
        self.constraint_type = None if constraint_type is None else mapNameToConstraintType(constraint_type)
        self.maintain_offset = maintain_offset
        #which axes the kind's channels are narrowed to - full unless a caller
        #asks for less
        self.channels = channels if channels is not None else ConstraintChannels()

        #every Maya node this created, so a rebuild can clear them. The matrix
        #network is made of DG nodes, which deleting the component's transform
        #hierarchy does NOT take with it - they would otherwise accumulate.
        self.built_maya_nodes = []

        self.id = self.assembleStableId()
        self.node.constraints.append(self)

    def getKindValue(self):
        return enumValue(self.kind)

    def assembleStableId(self):
        key = "%s:%s:%s:%s" % (self.node.id, self.child, self.parent, self.getKindValue())
        return int.from_bytes(hashlib.sha1(key.encode()).digest()[:8], "big") >> 1

    def getConstraintType(self):
        if self.constraint_type is not None:
            return self.constraint_type

        #the owner does not have to be a component node - the Skinning tab's
        #containers own constraints too and carry no properties panel, so they
        #always pass a type explicitly and fall through to the default here
        properties = getattr(self.node, "properties", None)
        return getattr(properties, "constraint_type", ConstraintType.MATRIX)

    def getConstraintTypeValue(self):
        return enumValue(self.getConstraintType())

    def getNodeBaseName(self):
        return "%s_%sConstraint" % (self.child, self.getKindValue())

    def getDrivenAxes(self, channel):
        """The axes of one channel this constraint actually drives: what its kind
        owns, narrowed by the channel mask."""
        translate, rotate, scale = KIND_CHANNELS[self.getKindValue()]
        #a parent constraint carries scale as well, in both techniques - the whole
        #matrix in matrix mode, a second scaleConstraint natively
        if self.getKindValue() == ConstraintKind.PARENT.value:
            scale = True

        owned = {"translate": translate, "rotate": rotate, "scale": scale}[channel]
        return self.channels.getAxes(channel) if owned else ""

    def drivesAnything(self):
        return any(self.getDrivenAxes(channel) for channel in ConstraintChannels.CHANNELS)

    def usesOffsetParentMatrix(self):
        #offsetParentMatrix is all or nothing, so a masked parent constraint has
        #to drive the channels one by one instead
        return self.getKindValue() == ConstraintKind.PARENT.value and self.channels.isFull()

    def exists(self):
        return any(MC.objectExists(maya_node) for maya_node in self.built_maya_nodes)

    def remove(self, sweep_scene = True):
        #what this object built, plus anything in the scene tagged as this
        #constraint's network - a previous connect, or one from before a reload,
        #which this object never knew about. sweep_scene=False skips that query
        #for a caller about to sweep the whole component's tags anyway.
        tagged = MC.getNodesWithTag(ROSE_Names.built_for_attribute_name, self.id) if sweep_scene else []

        for maya_node in self.built_maya_nodes + tagged:
            if MC.objectExists(maya_node):
                MC.deleteNode(maya_node)
        self.built_maya_nodes = []

    def tagBuiltNodes(self):
        for maya_node in self.built_maya_nodes:
            MC.addTag(maya_node, ROSE_Names.built_for_attribute_name, self.id)
            MC.addTag(maya_node, ROSE_Names.built_by_attribute_name, self.node.id)

# Building

    def build(self):
        if not MC.objectExists(self.child):
            return False, "Constraint child '%s' does not exist" % self.child
        if not MC.objectExists(self.parent):
            return False, "Constraint parent '%s' does not exist" % self.parent

        #read BEFORE the previous network goes: deleting the network that drives
        #the child drops it back to its undriven pose, and an offset taken from
        #there would move the child somewhere else on every re-connect
        self.child_world_matrix = om.MMatrix(MC.getObjectWorldPositionMatrix(self.child))
        self.remove()

        #a mask can switch every axis off - then there is nothing to build, and
        #Maya would refuse a constraint skipping all of its axes anyway
        if not self.drivesAnything():
            log.debug("CONSTRAINT:: --build:: %s drives no axes, nothing built" % self)
            return True, ""

        if self.getConstraintTypeValue() == ConstraintType.NATIVE.value:
            result = self.buildNative()
        else:
            result = self.buildMatrix()

        self.tagBuiltNodes()
        return result

    def buildNative(self):
        self.built_maya_nodes = []

        if self.getKindValue() == ConstraintKind.PARENT.value:
            if self.getDrivenAxes("translate") or self.getDrivenAxes("rotate"):
                self.built_maya_nodes.append(MC.createParentConstraint(
                    self.parent, self.child, self.maintain_offset,
                    skip_translate = self.channels.getSkipped("translate"),
                    skip_rotate = self.channels.getSkipped("rotate")))

            #A parentConstraint carries translate and rotate ONLY - scale needs its own
            #node. Matrix mode passes the whole matrix, so the two techniques otherwise
            #disagree in a way that is easy to miss: everything looks right until
            #something upstream is scaled, and then the scale silently never arrives.
            if self.getDrivenAxes("scale"):
                self.built_maya_nodes.append(MC.createScaleConstraint(
                    self.parent, self.child, self.maintain_offset,
                    skip = self.channels.getSkipped("scale")))

            return True, ""

        builders = {
            ConstraintKind.POINT.value:  (MC.createPointConstraint, "translate"),
            ConstraintKind.ORIENT.value: (MC.createOrientConstraint, "rotate"),
            ConstraintKind.SCALE.value:  (MC.createScaleConstraint, "scale"),
            ConstraintKind.AIM.value:    (MC.createAimConstraint, "rotate"),
        }
        builder, channel = builders[self.getKindValue()]

        constraint_node = builder(self.parent, self.child, self.maintain_offset,
                                  skip = self.channels.getSkipped(channel))
        self.built_maya_nodes = [constraint_node]

        return True, ""

    def buildMatrix(self):
        if self.getKindValue() == ConstraintKind.AIM.value:
            #no clean matrix equivalent: aimMatrix solves a different problem and
            #its offset semantics don't match an aimConstraint's. Rather than ship
            #something that quietly behaves differently, aim uses the native node.
            log.debug("CONSTRAINT:: --buildMatrix:: aim has no matrix form, using the native constraint")
            return self.buildNative()

        offset_matrix = self.computeOffsetMatrix()

        mult_matrix_node = MC.createMultMatrixNode(self.getNodeBaseName())
        #the offset goes in whole rather than through a composeMatrix built from
        #translate/rotate/scale - that round trip drops shear and forces a rotate order
        MC.setMatrixAttribute(mult_matrix_node, "matrixIn[0]", offset_matrix)
        MC.connectAttribute(self.parent, "worldMatrix[0]", mult_matrix_node, "matrixIn[1]")
        self.built_maya_nodes = [mult_matrix_node]

        #the child's own parent has to be divided out *in the network*, not folded
        #into the constant: fold it in and the driver's movement gets conjugated by
        #the parent, which is correct at build time and wrong the moment the driver
        #moves.
        #
        #Deliberately the DAG parent's worldInverseMatrix and not the child's own
        #parentInverseMatrix: since Maya 2020 a node's parentMatrix *includes its
        #own offsetParentMatrix*, so reading parentInverseMatrix here would feed
        #the plug this network drives straight back into itself.
        self.connectChildParentInverse(mult_matrix_node)

        if self.usesOffsetParentMatrix():
            return self.connectAsOffsetParentMatrix(mult_matrix_node)

        return self.connectAsChannels(mult_matrix_node)

    def connectChildParentInverse(self, mult_matrix_node):
        child_parent = MC.getObjectParentNode(self.child)
        if not child_parent:
            #at the world root there is nothing to divide out, and leaving the
            #plug unconnected keeps it identity
            return
        MC.connectAttribute(child_parent[0], "worldInverseMatrix[0]", mult_matrix_node, "matrixIn[2]")

    def connectAsOffsetParentMatrix(self, mult_matrix_node):
        """Drive everything through offsetParentMatrix - one connection, no
        decompose, and the channel box stays free for the animator."""
        #forced: a rebuild, or a constraint replacing an earlier one on the same
        #child, should take over the plug rather than throw
        MC.connectAttribute(mult_matrix_node, "matrixSum", self.child, "offsetParentMatrix", force = True)
        MC.clearTransforms(self.child)
        return True, ""

    def connectAsChannels(self, mult_matrix_node):
        """Drive only the axes this constraint owns, so a point constraint leaves
        rotation alone and a masked one leaves its skipped axes alone.

        Axes left undriven keep whatever value they had, as with Maya's own skip
        flags."""
        translate_axes = self.getDrivenAxes("translate")
        rotate_axes = self.getDrivenAxes("rotate")
        scale_axes = self.getDrivenAxes("scale")

        #matrixIn[2] already put this in the child's parent space
        decompose_node = None
        if translate_axes or scale_axes:
            decompose_node = MC.createDecomposeNode(self.getNodeBaseName())
            MC.connectAttribute(mult_matrix_node, "matrixSum", decompose_node, "inputMatrix")
            self.built_maya_nodes.append(decompose_node)

        rotate_decompose_node = decompose_node
        if rotate_axes:
            source_node = mult_matrix_node

            joint_orient_inverse = self.getJointOrientInverseMatrix()
            if joint_orient_inverse is not None:
                #a joint applies jointOrient on top of rotate, so driving rotate
                #from the raw local matrix lands off by exactly that. Cancelling it
                #on the right leaves the upper 3x3 as the rotation we actually want.
                #
                #Rotation only: the same multiply also turns the translation row,
                #which is why translate keeps reading the uncancelled decompose.
                orient_node = MC.createMultMatrixNode(self.getNodeBaseName() + "_jointOrient")
                MC.connectAttribute(mult_matrix_node, "matrixSum", orient_node, "matrixIn[0]")
                MC.setMatrixAttribute(orient_node, "matrixIn[1]", joint_orient_inverse)
                self.built_maya_nodes.append(orient_node)
                source_node = orient_node

            if rotate_decompose_node is None or source_node is not mult_matrix_node:
                rotate_decompose_node = MC.createDecomposeNode(self.getNodeBaseName() + "_rotate")
                MC.connectAttribute(source_node, "matrixSum", rotate_decompose_node, "inputMatrix")
                self.built_maya_nodes.append(rotate_decompose_node)

            #the decompose has to read the child's own rotate order, not force one
            #onto it - the previous code drove the child's rotateOrder from the
            #decompose's unset input, pinning everything to XYZ
            MC.connectAttribute(self.child, "rotateOrder", rotate_decompose_node, "inputRotateOrder")

        for axis in translate_axes:
            MC.connectAttribute(decompose_node, "outputTranslate" + axis, self.child, "translate" + axis, force = True)
        for axis in rotate_axes:
            MC.connectAttribute(rotate_decompose_node, "outputRotate" + axis, self.child, "rotate" + axis, force = True)
        for axis in scale_axes:
            MC.connectAttribute(decompose_node, "outputScale" + axis, self.child, "scale" + axis, force = True)

        return True, ""

# Offset maths

    def getJointOrientInverseMatrix(self):
        joint_orient = MC.getJointOrient(self.child)
        if joint_orient is None:
            return None

        euler = om.MEulerRotation([om.MAngle(value, om.MAngle.kDegrees).asRadians()
                                   for value in joint_orient])
        return om.MTransformationMatrix().setRotation(euler).asMatrix().inverse()

    def getNeutralLocalMatrix(self):
        """The child's local matrix as it will be once its channels are zeroed.

        Identity for a plain transform; the jointOrient matrix for a joint, which
        Maya keeps applying even with translate/rotate/scale at zero. Left out of
        the offset, every matrix-constrained joint lands rotated by its own orient.
        """
        joint_orient_inverse = self.getJointOrientInverseMatrix()
        if joint_orient_inverse is None:
            return om.MMatrix()
        return joint_orient_inverse.inverse()

    def computeOffsetMatrix(self):
        if self.usesOffsetParentMatrix():
            #world = localMatrix x offsetParentMatrix x childParentWorld, so the
            #constant also cancels the neutral local matrix - for a joint that is
            #its jointOrient, which Maya keeps applying with the channels at zero.
            #
            #This is needed whether or not an offset is maintained: "no offset"
            #means the child should land exactly on the parent, and without the
            #cancellation it lands on the parent rotated by its own jointOrient.
            neutral_inverse = self.getNeutralLocalMatrix().inverse()

            if not self.maintain_offset:
                return neutral_inverse

            parent_world = om.MMatrix(MC.getObjectWorldPositionMatrix(self.parent))
            return neutral_inverse * self.child_world_matrix * parent_world.inverse()

        #channel kinds - and masked parents, which go the channel route - cancel
        #the jointOrient in the network instead (see connectAsChannels), so
        #identity really is the no-offset case here
        if not self.maintain_offset:
            return om.MMatrix()

        parent_world = om.MMatrix(MC.getObjectWorldPositionMatrix(self.parent))
        return self.child_world_matrix * parent_world.inverse()

    def __str__(self):
        return "constraint(%s -> %s, %s, %s, %s)" % (self.parent, self.child,
                                                     self.getKindValue(), self.getConstraintTypeValue(),
                                                     self.channels)
