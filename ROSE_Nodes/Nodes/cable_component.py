import maya.api.OpenMaya as om #type: ignore

from PySide6.QtWidgets import QHBoxLayout, QLabel, QSpinBox, QComboBox, QCheckBox #type: ignore

from MNRB.ROSE_Nodes.node_Editor_conf import TYPEID_CABLECOMPONENT, registerNode #type: ignore
from MNRB.ROSE_Nodes.rose_node_base import ROSE_Node, ROSE_NodeProperties #type: ignore
from MNRB.ROSE_Attributes.attribute_types import AttributeType #type: ignore
from MNRB.ROSE_Constraints.constraint_types import ConstraintType #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.ROSE_naming.ROSE_names import ROSE_Names #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_Guides.guide import guide #type: ignore
from MNRB.ROSE_Deform.deform import deform #type: ignore
from MNRB.ROSE_Controls.control import control #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

#how the controls between the two ends are carried
CONTROL_MODE_BLENDED = "blended"
CONTROL_MODE_FK = "fk"
CONTROL_MODE_LABELS = [(CONTROL_MODE_BLENDED, "Blended between ends"), (CONTROL_MODE_FK, "FK chain")]

#spacing of a fresh cable's guides, along X
GUIDE_SPACING = 5.0


class CableProperties(ROSE_NodeProperties):

    DEFAULT_DEFORM_COUNT = 8
    DEFAULT_CONTROL_COUNT = 4

    def __init__(self, node):
        #set before super(), which calls initUI() and reads them back
        self.deform_count = self.DEFAULT_DEFORM_COUNT
        self.control_count = self.DEFAULT_CONTROL_COUNT
        self.control_mode = CONTROL_MODE_BLENDED
        self.stretch_by_default = True
        super().__init__(node)

    def initUI(self):
        super().initUI()

        deform_row = QHBoxLayout()
        deform_row.addWidget(QLabel("Deforms:"))
        self.deform_count_spinbox = QSpinBox()
        self.deform_count_spinbox.setRange(2, 128)
        self.deform_count_spinbox.setValue(self.deform_count)
        self.deform_count_spinbox.setToolTip("Joints along the cable, spread evenly by length")
        self.deform_count_spinbox.valueChanged.connect(self.updateDeformCount)
        deform_row.addWidget(self.deform_count_spinbox)
        self.layout.addLayout(deform_row)

        control_row = QHBoxLayout()
        control_row.addWidget(QLabel("Controls:"))
        self.control_count_spinbox = QSpinBox()
        self.control_count_spinbox.setRange(2, 32)
        self.control_count_spinbox.setValue(self.control_count)
        self.control_count_spinbox.setToolTip("Controls shaping the curve - one guide each. The first and last "
                                              "are the cable's ends")
        self.control_count_spinbox.valueChanged.connect(self.updateControlCount)
        control_row.addWidget(self.control_count_spinbox)
        self.layout.addLayout(control_row)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Middle Controls:"))
        self.control_mode_combo = QComboBox()
        for mode, label in CONTROL_MODE_LABELS:
            self.control_mode_combo.addItem(label, mode)
        self.control_mode_combo.setCurrentIndex(max(self.control_mode_combo.findData(self.control_mode), 0))
        self.control_mode_combo.setToolTip("Blended: each middle control follows a mix of the start and end, "
                                           "by how far along it is - move an end and the cable follows.\n"
                                           "FK chain: each control follows the one before it.")
        self.control_mode_combo.currentIndexChanged.connect(self.updateControlMode)
        mode_row.addWidget(self.control_mode_combo)
        self.layout.addLayout(mode_row)

        self.stretch_checkbox = QCheckBox("Stretch by default")
        self.stretch_checkbox.setChecked(self.stretch_by_default)
        self.stretch_checkbox.setToolTip("The starting value of the cable's 'stretch' attribute. Stretching, the "
                                         "joints spread over the whole curve; not, they keep their spacing and "
                                         "run out before its end")
        self.stretch_checkbox.toggled.connect(self.updateStretchByDefault)
        self.layout.addWidget(self.stretch_checkbox)

    def updateDeformCount(self, value):
        if value == self.deform_count:
            return
        self.deform_count = value
        self.setNeedsRebuild(True, "Deform count changed")
        self.setHasBeenModified()

    def updateControlCount(self, value):
        if value == self.control_count:
            return
        self.control_count = value
        #one guide per control - the guides are what has to be rebuilt first
        self.setNeedsRebuild(True, "Control count changed - rebuild the guides")
        self.setHasBeenModified()

    def updateControlMode(self, index):
        mode = self.control_mode_combo.itemData(index)
        if mode == self.control_mode:
            return
        self.control_mode = mode
        self.setNeedsRebuild(True, "Middle control mode changed")
        self.setHasBeenModified()

    def updateStretchByDefault(self, checked):
        if checked == self.stretch_by_default:
            return
        self.stretch_by_default = checked
        self.node.refreshAttributes()
        self.setHasBeenModified()

    def serialize(self):
        result_data = super().serialize()
        result_data["deform_count"] = self.deform_count
        result_data["control_count"] = self.control_count
        result_data["control_mode"] = self.control_mode
        result_data["stretch_by_default"] = self.stretch_by_default
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True):
        result = super().deserialize(data, hashmap, restore_id)

        self.deform_count = data.get("deform_count", self.DEFAULT_DEFORM_COUNT)
        self.control_count = data.get("control_count", self.DEFAULT_CONTROL_COUNT)
        self.control_mode = data.get("control_mode", CONTROL_MODE_BLENDED)
        self.stretch_by_default = data.get("stretch_by_default", True)

        self.is_silent = True
        self.deform_count_spinbox.setValue(self.deform_count)
        self.control_count_spinbox.setValue(self.control_count)
        self.control_mode_combo.setCurrentIndex(max(self.control_mode_combo.findData(self.control_mode), 0))
        self.stretch_checkbox.setChecked(self.stretch_by_default)
        self.is_silent = False

        #the node re-declares its attributes itself once its id is restored too
        return result


@registerNode(TYPEID_CABLECOMPONENT)
class Cable(ROSE_Node):
    """A cable: any number of controls shaping a curve, any number of joints
    riding it.

    The controls are the curve's control points. Each joint sits on a motion
    path at its share of the curve's length, facing along it, and turned by an
    up vector blended from the two controls either side of it - so every
    control twists the stretch of cable around it, not only the ends.

    Stretch is an attribute from 0 to 1. At 1 the joints spread over the whole
    curve however long it gets; at 0 they keep their rest spacing and run out
    before its end when it is pulled longer.

    No spline IK: its twist comes from the two ends only, and a cable needs
    every control to twist it.
    """

    type_id = TYPEID_CABLECOMPONENT
    category = "rose.simple_components"
    operation_title = "Cable"
    icon = ""
    Node_Properties_Class = CableProperties

    #the last deform and output carry this name, as do the output sockets - a
    #downstream component resolves its parent from the socket name
    end_name = "end"

    start_input_index = 0
    parent_def_input_index = 1
    end_input_index = 2

    def __init__(self, scene):
        super().__init__(scene,
                         inputs = [["start", SocketTypes.srt, False],
                                   ["parent_def", SocketTypes.deform, False],
                                   #optional: unconnected, the far end rides with the start
                                   ["end", SocketTypes.srt, False]],
                         outputs = [[self.end_name, SocketTypes.srt, True],
                                    [self.end_name, SocketTypes.deform, True]])

    def initAttributes(self):
        super().initAttributes()
        self.exposeAttribute("stretch", AttributeType.FLOAT,
                             default_value = 1.0 if self.properties.stretch_by_default else 0.0,
                             minimum = 0.0, maximum = 1.0)

# Naming

    def getGuideNames(self):
        return ["point%d" % index for index in range(self.properties.control_count)]

    def getDeformNames(self):
        count = self.properties.deform_count
        return ["seg%d" % index for index in range(count - 1)] + [self.end_name]

# Guides

    def guideBuild(self):
        if not super().guideBuild():
            return False

        #a chain, so the connectors draw the cable's line; each one offset along
        #X from the one before on a fresh cable
        parent_guide = None
        for guide_name in self.getGuideNames():
            new_guide = guide(self, guide_name, parent_guide)
            if parent_guide is None:
                MC.parentObject(new_guide.name, self.guide_component_hierarchy)
            else:
                new_guide.setPosition(parent_guide.getPosition())
                MC.parentObject(new_guide.name, parent_guide.name)
                MC.clearTransforms(new_guide.name)
                MC.addTranslation(new_guide.name, GUIDE_SPACING, 0.0, 0.0)
            parent_guide = new_guide

        #a changed control count meets positions stored for the old one; the
        #first ones keep theirs, any new ones their default placement
        self.reconstructGuides()
        return True

    def getControlPoints(self):
        return [om.MVector(*component_guide.getPosition()[12:15]) for component_guide in self.guides]

# Build-time geometry

    def getCurveDegree(self, point_count):
        return min(3, point_count - 1)

    def getRestUp(self, points):
        """The world direction the joints' Z leans to at rest: up, unless the
        cable itself runs mostly up, then forward."""
        direction = (points[-1] - points[0])
        if direction.length() > 1e-6 and abs(direction.normal() * om.MVector(0, 1, 0)) > 0.9:
            return om.MVector(0, 0, 1)
        return om.MVector(0, 1, 0)

    def sampleRestCurve(self, points):
        """The rest curve through the guides, measured: its length, each
        joint's (position, tangent) at an even share of it, and each control's
        share of the length at the point of the curve nearest it."""
        temporary = MC.createCurveFromPoints("roseCableRestSample_tmp", [(p.x, p.y, p.z) for p in points],
                                             degree = self.getCurveDegree(len(points)))
        try:
            dag_path = om.MSelectionList().add(temporary).getDagPath(0).extendToShape()
            curve = om.MFnNurbsCurve(dag_path)
            length = curve.length()

            count = self.properties.deform_count
            samples = []
            for index in range(count):
                parameter = curve.findParamFromLength(length * index / float(count - 1))
                samples.append((om.MVector(curve.getPointAtParam(parameter, om.MSpace.kWorld)),
                                curve.tangent(parameter, om.MSpace.kWorld).normal()))

            control_fractions = []
            for point in points:
                _, parameter = curve.closestPoint(om.MPoint(point), space = om.MSpace.kWorld)
                control_fractions.append(curve.findLengthFromParam(parameter) / length if length > 0 else 0.0)
            #the ends are the ends, whatever a closest-point search rounds them to
            control_fractions[0], control_fractions[-1] = 0.0, 1.0
        finally:
            MC.deleteNode(temporary)

        return length, samples, control_fractions

    def buildFrame(self, position, tangent, rest_up):
        """X along the cable, Z as close to rest_up as that allows."""
        z_axis = rest_up - tangent * (rest_up * tangent)
        if z_axis.length() < 1e-6:
            z_axis = om.MVector(1, 0, 0) - tangent * tangent.x
        z_axis = z_axis.normal()
        y_axis = z_axis ^ tangent
        return [tangent.x, tangent.y, tangent.z, 0.0,
                y_axis.x, y_axis.y, y_axis.z, 0.0,
                z_axis.x, z_axis.y, z_axis.z, 0.0,
                position.x, position.y, position.z, 1.0]

    def getBracket(self, fraction, control_fractions):
        """(lower control, upper control, weight towards the upper) for a
        point that far along the cable."""
        for index in range(len(control_fractions) - 1):
            lower, upper = control_fractions[index], control_fractions[index + 1]
            if fraction <= upper + 1e-9 or index == len(control_fractions) - 2:
                span = upper - lower
                weight = (fraction - lower) / span if span > 1e-9 else 0.0
                return index, index + 1, min(max(weight, 0.0), 1.0)
        return 0, 1, 0.0

# Static

    def staticBuild(self):
        if not super().staticBuild():
            return False

        points = self.getControlPoints()
        rest_up = self.getRestUp(points)
        _, samples, _ = self.sampleRestCurve(points)

        previous = None
        for deform_name, (position, tangent) in zip(self.getDeformNames(), samples):
            new_deform = deform(self, deform_name)
            new_deform.setPosition(self.buildFrame(position, tangent, rest_up))
            new_deform.setSegmentScaleCompensate(False)
            if previous is None:
                MC.parentObject(new_deform.name, self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name)
            else:
                MC.parentObject(new_deform.name, previous.name)
            previous = new_deform

        return True

# Component

    def componentBuild(self):
        if not super().componentBuild():
            return False

        prefix = self.getComponentFullPrefix()
        points = self.getControlPoints()
        rest_up = self.getRestUp(points)
        rest_length, samples, control_fractions = self.sampleRestCurve(points)

        self.start_input = self.createInput("start", points[0])
        self.end_input = self.createInput("end", points[-1])

        self.buildControls(points, control_fractions)
        self.buildCurve()
        self.buildStretch(rest_length)
        self.buildJoints(samples, control_fractions, rest_up)

        return True

    def createInput(self, name, position):
        transform = MC.createTransform(self.getComponentFullPrefix() + name + ROSE_Names.input_suffix)
        MC.parentObject(transform, self.input_hierarchy)
        MC.setObjectWorldPositionMatrix(transform, self.getWorldAlignedMatrix(position))
        return transform

    def getWorldAlignedMatrix(self, position):
        return [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, position.x, position.y, position.z, 1.0]

    def buildControls(self, points, control_fractions):
        """World-aligned controls on the guides. The first follows the start
        input, the last the end input; the ones between depend on the mode."""
        last = len(points) - 1
        self.cable_controls = []

        for index, point in enumerate(points):
            new_control = control(self, "point%d" % index)
            new_control.setPosition(self.getWorldAlignedMatrix(point))
            MC.parentObject(new_control.name, self.control_hierarchy)

            if index == 0:
                driver = self.start_input
            elif index == last:
                driver = self.end_input
            elif self.properties.control_mode == CONTROL_MODE_FK:
                driver = self.cable_controls[index - 1].name
            else:
                driver = self.buildBlendedSpace(index, point, control_fractions[index])

            #forced to matrix: an animator-facing control has to stay posable
            self.constrain(new_control.name, driver,
                           maintain_offset = True, constraint_type = ConstraintType.MATRIX)
            self.cable_controls.append(new_control)

    def buildBlendedSpace(self, index, point, fraction):
        """Where a middle control rides: its rest place as carried by the start,
        blended towards its rest place as carried by the end, by how far along
        the cable it sits."""
        prefix = self.getComponentFullPrefix()
        name = prefix + "point%dSpace" % index
        rest = om.MMatrix(self.getWorldAlignedMatrix(point))

        carried = []
        for end_input in (self.start_input, self.end_input):
            offset = rest * om.MMatrix(MC.getObjectWorldPositionMatrix(end_input)).inverse()
            carry = self.trackBuiltNode(MC.createMultMatrixNode(name + ("Start" if end_input == self.start_input else "End")))
            MC.setMatrixAttribute(carry, "matrixIn[0]", offset)
            MC.connectAttribute(end_input, "worldMatrix[0]", carry, "matrixIn[1]")
            carried.append(carry)

        blend = self.trackBuiltNode(MC.createBlendMatrixNode(name + "Blend"))
        MC.connectAttribute(carried[0], "matrixSum", blend, "inputMatrix")
        MC.connectAttribute(carried[1], "matrixSum", blend, "target[0].targetMatrix")
        MC.setAttribute(blend, "target[0].weight", fraction)

        local = self.trackBuiltNode(MC.createMultMatrixNode(name + "Local"))
        MC.connectAttribute(blend, "outputMatrix", local, "matrixIn[0]")
        MC.connectAttribute(self.system_hierarchy, "worldInverseMatrix[0]", local, "matrixIn[1]")

        space = MC.createTransform(name + "_srt")
        MC.parentObject(space, self.system_hierarchy)
        MC.connectAttribute(local, "matrixSum", space, "offsetParentMatrix", force = True)
        MC.clearTransforms(space)
        return space

    def buildCurve(self):
        prefix = self.getComponentFullPrefix()
        points = [MC.getObjectWorldPositionMatrix(c.name)[12:15] for c in self.cable_controls]

        self.curve = MC.createCurveFromPoints(prefix + "cable_crv", points, degree = self.getCurveDegree(len(points)))
        MC.parentObject(self.curve, self.system_hierarchy)
        self.curve_shape = MC.getObjectShapeNode(self.curve)

        #each control point is its control's position, in the systems group's space
        for index, cable_control in enumerate(self.cable_controls):
            to_curve = self.trackBuiltNode(MC.createPointMatrixMultNode(prefix + "cablePoint%d" % index))
            MC.connectAttribute(cable_control.name, "worldMatrix[0]", to_curve, "inMatrix")
            local = self.trackBuiltNode(MC.createPointMatrixMultNode(prefix + "cablePoint%dLocal" % index))
            MC.connectAttribute(to_curve, "output", local, "inPoint")
            MC.connectAttribute(self.system_hierarchy, "worldInverseMatrix[0]", local, "inMatrix")
            MC.connectAttribute(local, "output", self.curve_shape, "controlPoints[%d]" % index, force = True)

    def buildStretch(self, rest_length):
        """keep = rest length / current length: the share of the curve the
        joints cover when they keep their spacing. Measured against the start
        input's scale, so scaling the rig is not read as stretching the cable."""
        prefix = self.getComponentFullPrefix()

        curve_info = self.trackBuiltNode(MC.createCurveInfoNode(prefix + "cableLength"))
        MC.connectAttribute(self.curve_shape, "worldSpace[0]", curve_info, "inputCurve")

        self.rig_scale = self.trackBuiltNode(MC.createDecomposeNode(prefix + "cableScale"))
        MC.connectAttribute(self.start_input, "worldMatrix[0]", self.rig_scale, "inputMatrix")

        scaled_rest = self.trackBuiltNode(MC.createMathMultiplyNode(prefix + "cableRestLength"))
        MC.setAttribute(scaled_rest, "input[0]", rest_length)
        MC.connectAttribute(self.rig_scale, "outputScaleX", scaled_rest, "input[1]")

        self.keep_share = self.trackBuiltNode(MC.createDivideNode(prefix + "cableKeepShare"))
        MC.connectAttribute(scaled_rest, "output", self.keep_share, "input1")
        MC.connectAttribute(curve_info, "arcLength", self.keep_share, "input2")

    def buildJoints(self, samples, control_fractions, rest_up):
        prefix = self.getComponentFullPrefix()
        count = len(samples)

        #each control's up direction, carried by the control: its rest up in
        #its own space, so turning the control about the cable turns it
        control_ups = []
        for index, cable_control in enumerate(self.cable_controls):
            control_matrix = om.MMatrix(MC.getObjectWorldPositionMatrix(cable_control.name))
            up_in_control = (rest_up * control_matrix.inverse()).normal()
            up = self.trackBuiltNode(MC.createVectorProductNode(prefix + "point%dUp" % index))
            MC.setAttribute(up, "operation", 3)          #vector matrix product
            MC.setAttribute(up, "normalizeOutput", 1)
            for axis, value in zip("XYZ", (up_in_control.x, up_in_control.y, up_in_control.z)):
                MC.setAttribute(up, "input1" + axis, value)
            MC.connectAttribute(cable_control.name, "worldMatrix[0]", up, "matrix")
            control_ups.append(up)

        self.deform_outputs = []
        self.motion_paths = []
        for index, deform_name in enumerate(self.getDeformNames()):
            fraction = index / float(count - 1)
            name = prefix + "%sPath" % deform_name

            #where along the curve: `fraction` stretching, fraction * keep (never
            #past the end) keeping the spacing, blended by the stretch attribute
            kept = self.trackBuiltNode(MC.createMathMultiplyNode(name + "Kept"))
            MC.setAttribute(kept, "input[0]", fraction)
            MC.connectAttribute(self.keep_share, "output", kept, "input[1]")

            kept_on_curve = self.trackBuiltNode(MC.createClampNode(name + "KeptOnCurve"))
            MC.connectAttribute(kept, "output", kept_on_curve, "inputR")
            MC.setAttribute(kept_on_curve, "maxR", 1.0)

            position = self.trackBuiltNode(MC.createBlendColorsNode(name + "Position"))
            MC.setAttribute(position, "color1R", fraction)
            MC.connectAttribute(kept_on_curve, "outputR", position, "color2R")
            MC.connectAttribute(self.component_hierarchy, "stretch", position, "blender")

            #the up vector, from the two controls either side
            lower, upper, weight = self.getBracket(fraction, control_fractions)
            up = self.trackBuiltNode(MC.createBlendColorsNode(name + "Up"))
            MC.connectAttribute(control_ups[upper], "output", up, "color1")
            MC.connectAttribute(control_ups[lower], "output", up, "color2")
            MC.setAttribute(up, "blender", weight)

            motion_path = self.trackBuiltNode(MC.createMotionPathNode(name))
            MC.connectAttribute(self.curve_shape, "worldSpace[0]", motion_path, "geometryPath")
            MC.connectAttribute(position, "outputR", motion_path, "uValue")
            MC.setAttribute(motion_path, "fractionMode", 1)     #by length, not by parameter
            MC.setAttribute(motion_path, "follow", 1)
            MC.setAttribute(motion_path, "frontAxis", 0)        #X along the cable
            MC.setAttribute(motion_path, "upAxis", 2)           #Z towards the up vector
            MC.setAttribute(motion_path, "worldUpType", 3)      #Vector
            MC.connectAttribute(up, "output", motion_path, "worldUpVector")
            self.motion_paths.append(motion_path)

            #the joint's matrix: the path's position and turn, the rig's scale
            composed = self.trackBuiltNode(MC.createComposeNode(name + "Matrix"))
            MC.connectAttribute(motion_path, "allCoordinates", composed, "inputTranslate")
            MC.connectAttribute(motion_path, "rotate", composed, "inputRotate")
            MC.connectAttribute(self.rig_scale, "outputScale", composed, "inputScale")

            self.deform_outputs.append(self.createMatrixOutput(deform_name, composed))

    def createMatrixOutput(self, output_name, compose_node):
        prefix = self.getComponentFullPrefix()
        output = MC.createTransform(prefix + output_name + ROSE_Names.output_suffix)
        MC.parentObject(output, self.output_hierarchy)

        #the outputs group need not sit at the origin
        local_matrix = self.trackBuiltNode(MC.createMultMatrixNode(prefix + output_name + "OutputLocal"))
        MC.connectAttribute(compose_node, "outputMatrix", local_matrix, "matrixIn[0]")
        MC.connectAttribute(self.output_hierarchy, "worldInverseMatrix[0]", local_matrix, "matrixIn[1]")

        MC.connectAttribute(local_matrix, "matrixSum", output, "offsetParentMatrix", force = True)
        MC.clearTransforms(output)
        return output

# Connect

    def connectInputs(self):
        connected = True

        start_parent = None
        if self.isInputSocketConnected(self.start_input_index):
            start_parent = self.getInputConnectionValueAt(self.start_input_index)
        if start_parent is not None:
            self.constrain(self.start_input, start_parent + ROSE_Names.output_suffix, maintain_offset = True)
        else:
            connected = False

        if self.isInputSocketConnected(self.parent_def_input_index):
            deform_parent = self.getInputConnectionValueAt(self.parent_def_input_index)
            MC.parentObject(self.getOrderedDeforms()[0].name, deform_parent + ROSE_Names.deform_suffix)
        else:
            connected = False

        #optional - unconnected, the far end rides with the start
        if self.isInputSocketConnected(self.end_input_index):
            end_parent = self.getInputConnectionValueAt(self.end_input_index)
            self.constrain(self.end_input, end_parent + ROSE_Names.output_suffix, maintain_offset = True)
        elif start_parent is not None:
            self.constrain(self.end_input, start_parent + ROSE_Names.output_suffix, maintain_offset = True)

        return connected

    def getOrderedDeforms(self):
        """The joints start to end. Looked up by name rather than kept from
        staticBuild, which a reopened project has not run in this session."""
        by_name = {component_deform.deform_name: component_deform for component_deform in self.deforms}
        names = self.getDeformNames()
        missing = [name for name in names if name not in by_name]
        if missing:
            raise RuntimeError("%s has no %s deform(s) - rebuild the static and component steps together "
                               "after changing the deform count" % (self.__class__.__name__, ", ".join(missing)))
        return [by_name[name] for name in names]

    def connectDeforms(self):
        for component_deform, output in zip(self.getOrderedDeforms(), self.deform_outputs):
            #cleared before constraining: the constraint bakes the joint's
            #orientation into its offset
            MC.resetJointOrientations(component_deform.name)
            self.constrainDeform(component_deform.name, output, maintain_offset = False)
        return True
