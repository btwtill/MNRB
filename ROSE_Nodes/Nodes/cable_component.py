import maya.api.OpenMaya as om #type: ignore

from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QComboBox, QCheckBox, #type: ignore
                               QPushButton, QSlider, QWidget)
from PySide6.QtCore import Qt #type: ignore

from MNRB.ROSE_Nodes.node_Editor_conf import TYPEID_CABLECOMPONENT, registerNode #type: ignore
from MNRB.ROSE_Nodes.rose_node_base import ROSE_Node, ROSE_NodeProperties, deleteNodesTogether #type: ignore
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

#spacing of a fresh cable's shape points, along X
SHAPE_POINT_SPACING = 5.0

#tag on the guide stage's DG nodes - separate from the build tag, so a
#component build does not take them with it
GUIDE_PREVIEW_TAG = "rose_guide_preview"
#the shape points: locators, picked and moved by hand to shape the curve
SHAPE_POINT_COLOR = (0.35, 0.8, 1.0)
SHAPE_POINT_SIZE = 0.8

#the position sliders' resolution along the cable
POSITION_SLIDER_STEPS = 1000
#the least gap kept between neighbouring controls, as a share of the length
MINIMUM_CONTROL_GAP = 0.01


def getEvenFractions(count):
    return [index / float(count - 1) for index in range(count)]


class CableProperties(ROSE_NodeProperties):

    DEFAULT_DEFORM_COUNT = 8
    DEFAULT_CONTROL_COUNT = 4
    DEFAULT_SHAPE_POINT_COUNT = 5

    def __init__(self, node):
        #set before super(), which calls initUI() and reads them back
        self.deform_count = self.DEFAULT_DEFORM_COUNT
        self.control_count = self.DEFAULT_CONTROL_COUNT
        self.shape_point_count = self.DEFAULT_SHAPE_POINT_COUNT
        self.control_mode = CONTROL_MODE_BLENDED
        self.stretch_by_default = True
        #where each control sits along the cable, as a share of its length. The
        #ends are always 0 and 1; the middle ones slide between their neighbours
        self.control_fractions = getEvenFractions(self.DEFAULT_CONTROL_COUNT)
        #the shape points' world positions, [x, y, z] each. Saved with the
        #project: unlike guides, the locators are not something the guide
        #rebuild knows to carry over, and a fresh scene would lose the shape
        self.shape_points = []
        self.position_sliders = []
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

        shape_row = QHBoxLayout()
        shape_row.addWidget(QLabel("Shape Points:"))
        self.shape_point_spinbox = QSpinBox()
        self.shape_point_spinbox.setRange(2, 64)
        self.shape_point_spinbox.setValue(self.shape_point_count)
        self.shape_point_spinbox.setToolTip("Locators that shape the cable's curve - its control points. More "
                                            "of them, a more detailed shape; changing the count keeps the "
                                            "current shape. They are for shaping only: the controls sit on the "
                                            "finished curve")
        self.shape_point_spinbox.valueChanged.connect(self.updateShapePointCount)
        shape_row.addWidget(self.shape_point_spinbox)
        self.layout.addLayout(shape_row)

        fit_row = QHBoxLayout()
        self.fit_button = QPushButton("Fit to Selected Curve")
        self.fit_button.setToolTip("Place the shape points from a curve selected in the viewport - any curve, "
                                   "any number of points. It is rebuilt to the Shape Points count; the "
                                   "selected curve itself is left untouched")
        self.fit_button.clicked.connect(self.onFitToSelectedCurve)
        fit_row.addWidget(self.fit_button)
        self.flip_button = QPushButton("Flip Direction")
        self.flip_button.setToolTip("Swap which end the cable starts from")
        self.flip_button.clicked.connect(self.onFlipDirection)
        fit_row.addWidget(self.flip_button)
        self.layout.addLayout(fit_row)

        #what the last fit did - how close it came, or why it could not
        self.fit_result_label = QLabel("")
        self.fit_result_label.setWordWrap(True)
        self.fit_result_label.setVisible(False)
        self.layout.addWidget(self.fit_result_label)

        control_row = QHBoxLayout()
        control_row.addWidget(QLabel("Controls:"))
        self.control_count_spinbox = QSpinBox()
        self.control_count_spinbox.setRange(2, 32)
        self.control_count_spinbox.setValue(self.control_count)
        self.control_count_spinbox.setToolTip("Animation controls along the shaped curve - the guides on it. The "
                                              "first and last are the cable's ends; the ones between are slid "
                                              "along it with the sliders below")
        self.control_count_spinbox.valueChanged.connect(self.updateControlCount)
        control_row.addWidget(self.control_count_spinbox)
        self.layout.addLayout(control_row)

        #one slider per middle control - the ends are the cable's ends
        self.positions_widget = QWidget()
        self.positions_layout = QVBoxLayout(self.positions_widget)
        self.positions_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.positions_widget)

        self.even_button = QPushButton("Space Controls Evenly")
        self.even_button.clicked.connect(self.onSpaceControlsEvenly)
        self.layout.addWidget(self.even_button)
        self.rebuildPositionSliders()

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
        #a new count starts evenly spaced - the old positions were for other controls
        self.control_fractions = getEvenFractions(value)
        self.rebuildPositionSliders()
        #the control guides are redrawn straight away; the built cable needs a rebuild
        self.node.refreshGuideStage()
        self.setNeedsRebuild(True, "Control count changed")
        self.setHasBeenModified()

# Control positions

    def getControlFractions(self):
        """The stored positions, if they fit the count - evenly spaced otherwise."""
        fractions = list(self.control_fractions or [])
        if len(fractions) != self.control_count:
            fractions = getEvenFractions(self.control_count)
        fractions[0], fractions[-1] = 0.0, 1.0
        return fractions

    def rebuildPositionSliders(self):
        while self.positions_layout.count():
            item = self.positions_layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        self.position_sliders = []

        fractions = self.getControlFractions()
        for index in range(1, self.control_count - 1):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.addWidget(QLabel("Control %d:" % index))

            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, POSITION_SLIDER_STEPS)
            slider.setValue(int(round(fractions[index] * POSITION_SLIDER_STEPS)))
            slider.setToolTip("Where along the cable this control sits - it slides between its neighbours")
            value_label = QLabel("%.2f" % fractions[index])
            value_label.setMinimumWidth(32)
            slider.valueChanged.connect(lambda value, index = index, label = value_label:
                                        self.onControlPositionChanged(index, value, label))
            slider.sliderReleased.connect(self.onControlPositionReleased)

            row_layout.addWidget(slider, 1)
            row_layout.addWidget(value_label)
            self.positions_layout.addWidget(row)
            self.position_sliders.append(slider)

        #nothing to space with only the two ends
        self.even_button.setVisible(self.control_count > 2)

    def onControlPositionChanged(self, index, slider_value, value_label):
        fractions = self.getControlFractions()
        #held between its neighbours, so the controls never pass each other
        lowest = fractions[index - 1] + MINIMUM_CONTROL_GAP
        highest = fractions[index + 1] - MINIMUM_CONTROL_GAP
        fraction = min(max(slider_value / float(POSITION_SLIDER_STEPS), lowest), highest)

        clamped_value = int(round(fraction * POSITION_SLIDER_STEPS))
        if clamped_value != slider_value:
            slider = self.position_sliders[index - 1]
            slider.blockSignals(True)
            slider.setValue(clamped_value)
            slider.blockSignals(False)

        fractions[index] = fraction
        self.control_fractions = fractions
        value_label.setText("%.2f" % fraction)
        #the control's guide slides along the curve with it, live
        self.node.updateControlGuide(index, fraction)

    def onControlPositionReleased(self):
        self.setNeedsRebuild(True, "Control positions changed")
        self.setHasBeenModified()

    def onSpaceControlsEvenly(self):
        self.control_fractions = getEvenFractions(self.control_count)
        self.rebuildPositionSliders()
        for index, fraction in enumerate(self.control_fractions):
            self.node.updateControlGuide(index, fraction)
        self.setNeedsRebuild(True, "Control positions changed")
        self.setHasBeenModified()

# Fitting

    def onFitToSelectedCurve(self):
        success, message = self.node.fitShapeGuidesToSelectedCurve()
        self.showFitResult(message, success)
        if success:
            self.setNeedsRebuild(True, "Shape fitted to a curve")
            self.setHasBeenModified()

    def onFlipDirection(self):
        success, message = self.node.flipShapePoints()
        self.showFitResult(message, success)
        if success:
            #the controls keep their places on the cable - measured from the
            #other end now
            self.control_fractions = [1.0 - fraction for fraction in reversed(self.getControlFractions())]
            self.rebuildPositionSliders()
            for index, fraction in enumerate(self.control_fractions):
                self.node.updateControlGuide(index, fraction)
            self.setNeedsRebuild(True, "Cable direction flipped")
            self.setHasBeenModified()

    def showFitResult(self, message, success):
        self.fit_result_label.setText(message)
        self.fit_result_label.setStyleSheet("" if success else "color: #FFE0A030;")
        self.fit_result_label.setVisible(bool(message))

    def updateShapePointCount(self, value):
        if value == self.shape_point_count:
            return
        self.shape_point_count = value
        #redrawn straight away, resampled from the current shape - the curve
        #keeps its course with more or fewer points to hold it
        self.node.refreshGuideStage()
        self.setNeedsRebuild(True, "Shape point count changed")
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
        result_data["shape_point_count"] = self.shape_point_count
        result_data["control_mode"] = self.control_mode
        result_data["stretch_by_default"] = self.stretch_by_default
        result_data["control_fractions"] = self.getControlFractions()
        result_data["shape_points"] = [list(point) for point in self.node.getShapePointPositions()]
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True):
        result = super().deserialize(data, hashmap, restore_id)

        self.deform_count = data.get("deform_count", self.DEFAULT_DEFORM_COUNT)
        self.control_count = data.get("control_count", self.DEFAULT_CONTROL_COUNT)
        #cables saved before shaping and controls were separate had one guide
        #per control
        self.shape_point_count = data.get("shape_point_count", self.control_count)
        self.control_mode = data.get("control_mode", CONTROL_MODE_BLENDED)
        self.stretch_by_default = data.get("stretch_by_default", True)
        #cables saved before controls could be placed were evenly spaced
        self.control_fractions = data.get("control_fractions", getEvenFractions(self.control_count))
        #older saves kept the shape in their guides only - picked up from the
        #scene on the next guide build, see Cable.collectShapePoints
        self.shape_points = data.get("shape_points", [])

        self.is_silent = True
        self.deform_count_spinbox.setValue(self.deform_count)
        self.control_count_spinbox.setValue(self.control_count)
        self.shape_point_spinbox.setValue(self.shape_point_count)
        self.control_mode_combo.setCurrentIndex(max(self.control_mode_combo.findData(self.control_mode), 0))
        self.stretch_checkbox.setChecked(self.stretch_by_default)
        self.rebuildPositionSliders()
        self.is_silent = False

        #the node re-declares its attributes itself once its id is restored too
        return result


@registerNode(TYPEID_CABLECOMPONENT)
class Cable(ROSE_Node):
    """A cable: a shaped curve, controls on it, and joints riding it.

    Shaping and animating are separate. In the guide stage the guides are the
    curve's control points - shape handles - with the curve itself drawn live
    through them and a marker on it wherever a control will go. So what is
    shaped is exactly the curve the joints will run along, not a hull the
    curve only passes near.

    In the rig, the controls sit on that curve, evenly spread by length and
    turned along it. Each of the curve's control points is carried by the two
    controls either side of it, blended by how far along the cable it lies: at
    rest the curve is the shaped one exactly, and moving a control bends the
    cable around it. Only a control's position carries the curve - turning it
    twists the cable without bending it.

    Each joint sits on a motion path at its share of the curve's length, facing
    along it, and turned by an up vector blended from the two controls either
    side of it - so every control twists the stretch of cable around it.

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
        """One guide per control - where it will sit on the cable."""
        return ["point%d" % index for index in range(self.properties.control_count)]

    def getControlFractions(self):
        """Where the controls sit, as shares of the curve's length."""
        return self.properties.getControlFractions()

    def getDeformNames(self):
        count = self.properties.deform_count
        return ["seg%d" % index for index in range(count - 1)] + [self.end_name]

    def getShapePointName(self, index):
        return self.getComponentFullPrefix() + "shape%d_loc" % index

# Guides

    def guideBuild(self):
        """The guide stage: shape points, the curve through them, and a guide
        on it for every control.

        The shape points are locators - they are moved by hand to shape the
        curve, and are only that. The guides show where each control will sit
        and which way it will face, carried along the curve by the position
        sliders; they cannot be pulled off it.
        """
        #read before the base class deletes the guide group they live in
        shape_points = self.collectShapePoints()
        self.removeGuidePreview()

        if not super().guideBuild():
            return False

        self.properties.shape_points = shape_points
        self.buildShapePoints(shape_points)
        self.buildPreviewCurves()

        for guide_name in self.getGuideNames():
            new_guide = guide(self, guide_name, None)
            MC.parentObject(new_guide.name, self.guide_component_hierarchy)
            MC.clearTransforms(new_guide.name)
        self.attachControlGuides(shape_points)

        #no reconstructGuides(): the guides' places come from the sliders, and
        #they are driven along the curve - restoring a stored position onto
        #them would only fight that
        return True

    def isGuideStageBuilt(self):
        return bool(self.guide_component_hierarchy) and MC.objectExists(self.guide_component_hierarchy) \
            and self.isAllGuidesExistend()

    def refreshGuideStage(self):
        """Redraw the guide stage with the current counts, if it is up.

        Keeps the viewport selection: this runs from the properties panel, in
        the middle of the user's work, and creating the stage's nodes selects
        them - a curve picked for Fit was lost to a Shape Points change.
        """
        if not self.isGuideStageBuilt():
            return
        selection = MC.getViewportSelection(long_names = True)
        self.guideBuild()
        MC.restoreSelection(selection)

# Shape points

    def readLiveShapePoints(self):
        """The shape point locators' positions, if there are any in the scene."""
        points = []
        while MC.objectExists(self.getShapePointName(len(points))):
            points.append(tuple(MC.getObjectWorldTranslation(self.getShapePointName(len(points)))))
        return points if len(points) >= 2 else None

    def readLegacyShapeGuides(self):
        """Cables built before the swap shaped their curve with guides named
        shape0, shape1... - read once, the first time such a cable meets the
        new guide stage."""
        legacy = [g for g in self.guides if g.guide_name.startswith("shape") and g.exists()]
        if len(legacy) < 2:
            return None
        return [tuple(g.getPosition()[12:15]) for g in legacy]

    def collectShapePoints(self):
        """The shape, from wherever it is: the locators in the scene, a cable
        from before the swap, what was saved with the project - or a straight
        line for a fresh cable. Resampled to the Shape Points count."""
        points = self.readLiveShapePoints() or self.readLegacyShapeGuides()
        if points is None and len(self.properties.shape_points) >= 2:
            points = [tuple(point) for point in self.properties.shape_points]
        if points is None:
            points = [(SHAPE_POINT_SPACING * index, 0.0, 0.0)
                      for index in range(self.properties.shape_point_count)]
        return self.resamplePoints(points, self.properties.shape_point_count)

    def resamplePoints(self, points, count):
        """The same curve held by `count` control points instead."""
        if len(points) == count:
            return [tuple(point) for point in points]
        temporary = MC.createCurveFromPoints("roseCableResample_tmp", points,
                                             degree = self.getCurveDegree(len(points)))
        try:
            return MC.getRebuiltCurvePoints(temporary, count, self.getCurveDegree(count))
        finally:
            MC.deleteNode(temporary)

    def getShapePointPositions(self):
        """The current shape - live from the scene when the locators are up."""
        return self.readLiveShapePoints() or [tuple(point) for point in self.properties.shape_points]

    def setShapePoints(self, points):
        """Reshape the cable: store the points and move the locators there."""
        points = [tuple(point) for point in points]
        self.properties.shape_points = points
        live = self.readLiveShapePoints()
        if live is not None and len(live) == len(points):
            for index, point in enumerate(points):
                MC.setObjectWorldTranslation(self.getShapePointName(index), point)
        elif self.isGuideStageBuilt():
            self.guideBuild()

    def buildShapePoints(self, points):
        self.shape_point_locators = []
        for index, point in enumerate(points):
            locator = MC.createSpaceLocator((0, 0, 0), self.getShapePointName(index), SHAPE_POINT_COLOR)
            #directly under the guide group, so the preview curve can read its
            #translate as its own control point
            MC.parentObject(locator, self.guide_component_hierarchy)
            MC.clearTransforms(locator)
            MC.setObjectWorldTranslation(locator, point)
            MC.setLocatorLocalScale(locator, SHAPE_POINT_SIZE * self.properties.guide_size)
            self.shape_point_locators.append(locator)

    def getShapePoints(self):
        """The shape as vectors, for the build."""
        return [om.MVector(*point) for point in self.collectShapePoints()]

# Guide preview

    def removeGuidePreview(self):
        deleteNodesTogether(MC.getNodesWithTag(GUIDE_PREVIEW_TAG, self.id))

    def tagPreviewNode(self, maya_node):
        MC.addTag(maya_node, GUIDE_PREVIEW_TAG, self.id)
        return maya_node

    def buildPreviewCurves(self):
        """The cable's curve, live through the shape points, and its hull."""
        prefix = self.getComponentFullPrefix()
        #the hull - which point pulls where - thin and straight
        self.preview_hull = self.createPreviewCurve(prefix + "cableHull_preview", degree = 1)
        MC.setDisplayType(self.preview_hull, "template")
        #and the curve itself
        self.preview_curve = self.createPreviewCurve(prefix + "cable_preview",
                                                     degree = self.getCurveDegree(len(self.shape_point_locators)))

    def createPreviewCurve(self, name, degree):
        """A curve under the guide group whose control points are the shape
        point locators' own translate - they sit directly under the same
        group, so no conversion is needed."""
        points = [MC.getTranslation(locator) for locator in self.shape_point_locators]
        curve = MC.createCurveFromPoints(name, points, degree = degree)
        MC.parentObject(curve, self.guide_component_hierarchy)
        MC.clearTransforms(curve)
        curve_shape = MC.getObjectShapeNode(curve)
        for index, locator in enumerate(self.shape_point_locators):
            MC.connectAttribute(locator, "translate", curve_shape, "controlPoints[%d]" % index, force = True)
        MC.setDisplayType(curve, "reference")
        return curve

    def attachControlGuides(self, shape_points):
        """Each guide rides the preview curve at its control's position,
        facing along it - so it shows where the control will be and how it
        will be turned, and follows any reshaping live."""
        prefix = self.getComponentFullPrefix()
        preview_shape = MC.getObjectShapeNode(self.preview_curve)
        rest_up = self.getRestUp([om.MVector(*point) for point in shape_points])

        self.control_guide_paths = []
        for index, (component_guide, fraction) in enumerate(zip(self.guides, self.getControlFractions())):
            #the curve's local space is the guide group's, and so is the guide's
            path = self.tagPreviewNode(MC.createMotionPathNode(prefix + "point%dGuidePath" % index))
            MC.connectAttribute(preview_shape, "local", path, "geometryPath")
            MC.setAttribute(path, "fractionMode", 1)
            MC.setAttribute(path, "uValue", fraction)
            MC.setAttribute(path, "follow", 1)
            MC.setAttribute(path, "frontAxis", 0)        #X along the cable, as the control
            MC.setAttribute(path, "upAxis", 2)
            MC.setAttribute(path, "worldUpType", 3)
            for axis, value in zip("XYZ", (rest_up.x, rest_up.y, rest_up.z)):
                MC.setAttribute(path, "worldUpVector" + axis, value)
            MC.connectAttribute(path, "allCoordinates", component_guide.name, "translate", force = True)
            MC.connectAttribute(path, "rotate", component_guide.name, "rotate", force = True)
            #locked as well as driven: a connection alone still lets the move
            #tool drag the guide off the curve until the next evaluation snaps
            #it back. The sliders are how it moves.
            MC.lockAttributes(component_guide.name, ["translateX", "translateY", "translateZ",
                                                     "rotateX", "rotateY", "rotateZ"])
            self.control_guide_paths.append(path)

    def updateControlGuide(self, index, fraction):
        """Slide one control's guide along the curve, without rebuilding anything."""
        paths = getattr(self, "control_guide_paths", [])
        if index < len(paths) and MC.objectExists(paths[index]):
            MC.setAttribute(paths[index], "uValue", fraction)

# Fitting to a curve

    def fitShapeGuidesToSelectedCurve(self):
        """Place the shape points on a copy of the selected curve, rebuilt as a
        uniform curve with exactly as many control points. Returns (success,
        message)."""
        source = MC.getSelectedCurve()
        if source is None:
            return False, "Select a curve in the viewport first."
        if MC.isCurvePeriodic(source):
            return False, "'%s' is closed - a cable needs a start and an end." % source.split("|")[-1]

        count = self.properties.shape_point_count
        degree = self.getCurveDegree(count)
        points = MC.getRebuiltCurvePoints(source, count, degree)
        self.setShapePoints(points)

        deviation = self.measureFit(source, points, degree)
        message = "Fitted to '%s' - off by at most %.3f" % (source.split("|")[-1], deviation)
        if deviation > 0.05 * max(MC.getCurveLength(source), 1e-6) / max(count - 1, 1):
            message += ". Raise Shape Points for a closer fit."
        #the curve stays selected, so fitting again after a change is one click
        MC.clearSelection()
        MC.selectObject(source)
        return True, message

    def measureFit(self, source, points, degree):
        """The furthest the source curve strays from the fitted one."""
        fitted = MC.createCurveFromPoints("roseCableFitCheck_tmp", points, degree = degree)
        try:
            return MC.getMaximumCurveDeviation(source, fitted)
        finally:
            MC.deleteNode(fitted)

    def flipShapePoints(self):
        """Reverse the shape points' order - the start becomes the end."""
        points = self.getShapePointPositions()
        if len(points) < 2:
            return False, "Build the guides first."
        self.setShapePoints(list(reversed(points)))
        return True, "Flipped - the cable now starts at the other end."

# Mirroring

    def applyMirroredGuides(self, source_node):
        """Called by the editor's Mirror instead of setting guide positions:
        the guides here are carried along the curve, so it is the shape points
        that are mirrored - across X, like every other component's guides."""
        self.setShapePoints([(-x, y, z) for x, y, z in source_node.getShapePointPositions()])

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

    def sampleRestCurve(self, shape_points):
        """The shaped curve, measured. Returns its length, and (position,
        tangent) at an even share of it for each joint and for each control, and
        each control point's share of the length at the spot it pulls on most -
        its Greville abscissa, the average of the knots it spans."""
        degree = self.getCurveDegree(len(shape_points))
        temporary = MC.createCurveFromPoints("roseCableRestSample_tmp", [(p.x, p.y, p.z) for p in shape_points],
                                             degree = degree)
        try:
            dag_path = om.MSelectionList().add(temporary).getDagPath(0).extendToShape()
            curve = om.MFnNurbsCurve(dag_path)
            length = curve.length()

            def sampleAt(fraction):
                parameter = curve.findParamFromLength(length * fraction)
                return (om.MVector(curve.getPointAtParam(parameter, om.MSpace.kWorld)),
                        curve.tangent(parameter, om.MSpace.kWorld).normal())

            count = self.properties.deform_count
            joint_samples = [sampleAt(index / float(count - 1)) for index in range(count)]
            control_samples = [sampleAt(fraction) for fraction in self.getControlFractions()]

            knots = list(curve.knots())
            point_fractions = []
            for index in range(len(shape_points)):
                greville = sum(knots[index:index + degree]) / float(degree)
                point_fractions.append(curve.findLengthFromParam(greville) / length if length > 0 else 0.0)
            #the ends are the ends, whatever the arithmetic rounds them to
            point_fractions[0], point_fractions[-1] = 0.0, 1.0
        finally:
            MC.deleteNode(temporary)

        return length, joint_samples, control_samples, point_fractions

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

        shape_points = self.getShapePoints()
        rest_up = self.getRestUp(shape_points)
        _, joint_samples, _, _ = self.sampleRestCurve(shape_points)

        previous = None
        for deform_name, (position, tangent) in zip(self.getDeformNames(), joint_samples):
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

        shape_points = self.getShapePoints()
        rest_up = self.getRestUp(shape_points)
        rest_length, joint_samples, control_samples, point_fractions = self.sampleRestCurve(shape_points)
        control_fractions = self.getControlFractions()

        self.start_input = self.createInput("start", shape_points[0])
        self.end_input = self.createInput("end", shape_points[-1])

        control_frames = [self.buildFrame(position, tangent, rest_up) for position, tangent in control_samples]
        self.buildControls(control_frames, control_fractions)
        self.buildCurve(shape_points, point_fractions, control_fractions)
        self.buildStretch(rest_length)
        self.buildJoints(joint_samples, control_fractions, rest_up)

        return True

    def createInput(self, name, position):
        transform = MC.createTransform(self.getComponentFullPrefix() + name + ROSE_Names.input_suffix)
        MC.parentObject(transform, self.input_hierarchy)
        MC.setObjectWorldPositionMatrix(transform, self.getWorldAlignedMatrix(position))
        return transform

    def getWorldAlignedMatrix(self, position):
        return [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, position.x, position.y, position.z, 1.0]

    def buildControls(self, control_frames, control_fractions):
        """Controls on the shaped curve, X along it - so turning one about its
        own X twists the cable. The first follows the start input, the last the
        end input; the ones between depend on the mode."""
        last = len(control_frames) - 1
        self.cable_controls = []

        for index, frame in enumerate(control_frames):
            new_control = control(self, "point%d" % index)
            new_control.setPosition(frame)
            MC.parentObject(new_control.name, self.control_hierarchy)

            if index == 0:
                driver = self.start_input
            elif index == last:
                driver = self.end_input
            elif self.properties.control_mode == CONTROL_MODE_FK:
                driver = self.cable_controls[index - 1].name
            else:
                driver = self.buildBlendedSpace(index, frame, control_fractions[index])

            #forced to matrix: an animator-facing control has to stay posable
            self.constrain(new_control.name, driver,
                           maintain_offset = True, constraint_type = ConstraintType.MATRIX)
            self.cable_controls.append(new_control)

    def buildBlendedSpace(self, index, frame, fraction):
        """Where a middle control rides: its rest place as carried by the start,
        blended towards its rest place as carried by the end, by how far along
        the cable it sits."""
        prefix = self.getComponentFullPrefix()
        name = prefix + "point%dSpace" % index
        rest = om.MMatrix(frame)

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

    def buildCurve(self, shape_points, point_fractions, control_fractions):
        """The shaped curve, its control points carried by the controls.

        Each control point follows the two controls either side of the spot it
        pulls on, blended by where it lies between them - held in each one's
        space at its rest offset, so at rest nothing moves and the curve is the
        shaped one exactly."""
        prefix = self.getComponentFullPrefix()

        self.curve = MC.createCurveFromPoints(prefix + "cable_crv", [(p.x, p.y, p.z) for p in shape_points],
                                              degree = self.getCurveDegree(len(shape_points)))
        MC.parentObject(self.curve, self.system_hierarchy)
        self.curve_shape = MC.getObjectShapeNode(self.curve)

        #at rest a control's carrier is its world matrix - no local rotation yet
        control_inverses = [om.MMatrix(MC.getObjectWorldPositionMatrix(c.name)).inverse()
                            for c in self.cable_controls]
        carriers = [self.buildCarrier(index, c) for index, c in enumerate(self.cable_controls)]

        for index, (point, fraction) in enumerate(zip(shape_points, point_fractions)):
            name = prefix + "cablePoint%d" % index
            lower, upper, weight = self.getBracket(fraction, control_fractions)

            carried = []
            for control_index, suffix in ((lower, "Lower"), (upper, "Upper")):
                local_point = om.MPoint(point) * control_inverses[control_index]
                carry = self.trackBuiltNode(MC.createPointMatrixMultNode(name + suffix))
                for axis, value in zip("XYZ", (local_point.x, local_point.y, local_point.z)):
                    MC.setAttribute(carry, "inPoint" + axis, value)
                MC.connectAttribute(carriers[control_index], "matrixSum", carry, "inMatrix")
                carried.append(carry)

            blend = self.trackBuiltNode(MC.createBlendColorsNode(name + "Blend"))
            MC.connectAttribute(carried[1], "output", blend, "color1")
            MC.connectAttribute(carried[0], "output", blend, "color2")
            MC.setAttribute(blend, "blender", weight)

            #the curve lives under the systems group, which need not be at the origin
            local = self.trackBuiltNode(MC.createPointMatrixMultNode(name + "Local"))
            MC.connectAttribute(blend, "output", local, "inPoint")
            MC.connectAttribute(self.system_hierarchy, "worldInverseMatrix[0]", local, "inMatrix")
            MC.connectAttribute(local, "output", self.curve_shape, "controlPoints[%d]" % index, force = True)

    def buildCarrier(self, index, cable_control):
        """What carries the curve points near a control: its position, in the
        space it follows - but not its own rotation or scale.

        The curve points of a shaped cable sit well off the curve. Carried by
        the control's full matrix, turning the control about the cable to twist
        it swung those points around it and bent the whole curve. Twist is the
        up vectors' job (they do read the full matrix); the shape only moves
        with where the control is and what it hangs from."""
        prefix = self.getComponentFullPrefix()
        position = self.trackBuiltNode(MC.createComposeNode(prefix + "point%dPosition" % index))
        MC.connectAttribute(cable_control.name, "translate", position, "inputTranslate")

        #parentMatrix already includes the control's own offsetParentMatrix -
        #which is where the space it follows arrives - so it is all that is needed
        carrier = self.trackBuiltNode(MC.createMultMatrixNode(prefix + "point%dCarrier" % index))
        MC.connectAttribute(position, "outputMatrix", carrier, "matrixIn[0]")
        MC.connectAttribute(cable_control.name, "parentMatrix[0]", carrier, "matrixIn[1]")
        return carrier

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
