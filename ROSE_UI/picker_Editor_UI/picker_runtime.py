"""The rig picker an animator runs - and the drawing the ROSE editor shares with it.

This file is copied whole into the exported picker script, with the picker's
layout appended as PICKER_DATA. So it must stand alone: Maya and Qt only, no
ROSE. It runs on PySide6 (Maya 2025+) and PySide2.

The animator executes the exported file in the Script Editor (or from a
shelf). It asks which namespace the rig is referenced under - offering the ones
in the scene that actually hold this rig's controls - and opens the picker.

A button does one thing:
    select   select its controls (shift-click adds, ctrl-click toggles)
    builtin  run one of the ready-made actions below
    code     run the button's own Python

Button code runs with these names available:
    rig     the RigContext - rig.node("M_arm_ik_ctrl") is that control under the
            chosen namespace; see its methods below
    cmds    maya.cmds
    mel     maya.mel
Every click is one undo step, and an error in a button's code is reported in the
picker rather than taking it down.
"""

import json
import math
import traceback

try:
    from PySide6 import QtCore, QtGui, QtWidgets #type: ignore
    QT6 = True
except ImportError: #pragma: no cover - Maya 2024 and earlier
    from PySide2 import QtCore, QtGui, QtWidgets #type: ignore
    QT6 = False

try:
    import maya.cmds as cmds #type: ignore
    import maya.mel as mel #type: ignore
except ImportError: #pragma: no cover - outside Maya, only the drawing is used
    cmds = mel = None

PICKER_VERSION = 1

#the ready-made actions, by id: (label, description)
BUILTIN_ACTIONS = [
    ("reset_rig", "Reset Whole Rig", "Every control back to its default pose"),
    ("reset_selected", "Reset Selected", "The selected controls back to their default pose"),
    ("select_all", "Select All Controls", "Every control of the rig"),
    ("select_mirror", "Select Mirror", "Swap the selection for the other side's controls"),
    ("mirror_pose", "Mirror Pose To Other Side", "Copy the selected controls' pose onto the other side"),
    ("swap_pose", "Swap Pose Sides", "Exchange the pose of the selected controls and the other side's"),
    ("key_selected", "Key Selected", "Set a key on the selected controls' animatable channels"),
]
BUILTIN_LABELS = {action_id: label for action_id, label, _ in BUILTIN_ACTIONS}

DEFAULT_FONT_FAMILY = "Verdana"


# ---------------------------------------------------------------- drawing

def toColor(value, fallback = "#808080"):
    color = QtGui.QColor(value or fallback)
    return color if color.isValid() else QtGui.QColor(fallback)


def getContours(shape):
    """A polygon's outlines. One for a drawn polygon ("points"); several for an
    imported shape with holes or separate parts ("contours"), filled by its
    "fill_rule" - "evenodd" or "nonzero", as in SVG."""
    if shape.get("contours"):
        return shape["contours"]
    return [shape["points"]] if shape.get("points") else []


def buildShapePath(shape):
    """The shape's outline in its own space - origin at its top-left corner."""
    path = QtGui.QPainterPath()
    width, height = max(shape.get("w", 0), 1), max(shape.get("h", 0), 1)
    kind = shape.get("type")
    if kind == "ellipse":
        path.addEllipse(QtCore.QRectF(0, 0, width, height))
    elif kind == "polygon":
        for contour in getContours(shape):
            if len(contour) < 2:
                continue
            path.moveTo(*contour[0])
            for point in contour[1:]:
                path.lineTo(*point)
            path.closeSubpath()
        path.setFillRule(QtCore.Qt.OddEvenFill if shape.get("fill_rule") == "evenodd" else QtCore.Qt.WindingFill)
    else:
        radius = min(shape.get("radius", 0), width / 2.0, height / 2.0)
        path.addRoundedRect(QtCore.QRectF(0, 0, width, height), radius, radius)
    return path


def paintShape(painter, shape, highlight = 0.0):
    """Draw a shape at the painter's origin. `highlight` 0..1 lightens it - the
    picker's hover and press feedback."""
    painter.save()
    painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
    painter.setOpacity(shape.get("opacity", 1.0))
    path = buildShapePath(shape)

    fill = shape.get("fill") or {}
    outline = shape.get("outline") or {}
    if fill.get("enabled", True):
        color = toColor(fill.get("color"))
        if highlight:
            color = color.lighter(100 + int(60 * highlight))
        painter.setBrush(QtGui.QBrush(color))
    else:
        painter.setBrush(QtCore.Qt.NoBrush)
    if outline.get("enabled", False) and outline.get("width", 1) > 0:
        pen = QtGui.QPen(toColor(outline.get("color"), "#000000"))
        pen.setWidthF(outline.get("width", 1))
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        painter.setPen(pen)
    else:
        painter.setPen(QtCore.Qt.NoPen)
    if shape.get("type") != "text" or fill.get("enabled", False) or outline.get("enabled", False):
        painter.drawPath(path)

    text = shape.get("text") or {}
    if shape.get("type") == "text" and text.get("content"):
        font = QtGui.QFont(DEFAULT_FONT_FAMILY)
        font.setPixelSize(max(int(text.get("size", 12)), 1))
        font.setBold(bool(text.get("bold", False)))
        painter.setFont(font)
        painter.setPen(toColor(text.get("color"), "#FFFFFF"))
        alignment = {"left": QtCore.Qt.AlignLeft, "right": QtCore.Qt.AlignRight}.get(
            text.get("align"), QtCore.Qt.AlignHCenter)
        painter.drawText(QtCore.QRectF(0, 0, shape.get("w", 0), shape.get("h", 0)),
                         alignment | QtCore.Qt.AlignVCenter | QtCore.Qt.TextWordWrap, text["content"])
    painter.restore()


def shapeContains(shape, point):
    """Whether a point in page space is on the shape - the clickable area."""
    local = QtCore.QPointF(point.x() - shape.get("x", 0), point.y() - shape.get("y", 0))
    if shape.get("type") == "text":
        return QtCore.QRectF(0, 0, shape.get("w", 0), shape.get("h", 0)).contains(local)
    return buildShapePath(shape).contains(local)


# ---------------------------------------------------------------- the rig in the scene

class RigContext:
    """The rig as it sits in this scene - its controls under the chosen namespace.

    Button code gets this as `rig`. Use rig.node() for every rig object a script
    names: the rig's names are stored without a namespace, and this adds the one
    the animator picked."""

    def __init__(self, data, namespace = ""):
        self.data = data
        self.namespace = namespace.strip(":")
        mirror = data.get("mirror_prefixes") or [["L_", "R_"]]
        self.mirror_pairs = [tuple(pair) for pair in mirror]

    def node(self, name):
        """A rig object's name in this scene."""
        if not self.namespace or ":" in name.lstrip(":"):
            return name
        return "%s:%s" % (self.namespace, name)

    def nodes(self, *names):
        return [self.node(name) for name in names]

    def controls(self):
        """Every control of the rig, that exists in this scene."""
        return [self.node(name) for name in self.data.get("controls", []) if cmds.objExists(self.node(name))]

    def select(self, *names, **flags):
        """Select rig objects by their rig names - cmds.select's flags apply."""
        existing = [self.node(name) for name in names if cmds.objExists(self.node(name))]
        if existing:
            cmds.select(existing, **flags)
        elif not flags.get("add") and not flags.get("toggle"):
            cmds.select(clear = True)
        return existing

    def selectedControls(self):
        """The selected nodes that are controls of this rig."""
        rig_controls = set(self.controls())
        return [node for node in (cmds.ls(selection = True) or []) if node in rig_controls]

    def stripNamespace(self, name):
        prefix = self.namespace + ":" if self.namespace else ""
        return name[len(prefix):] if prefix and name.startswith(prefix) else name

    def mirrorName(self, name):
        """The other side's control for a name, or None. Works on names with or
        without the namespace."""
        short = self.stripNamespace(name)
        for left, right in self.mirror_pairs:
            for this, other in ((left, right), (right, left)):
                if short.startswith(this):
                    mirrored = self.node(other + short[len(this):])
                    return mirrored if cmds.objExists(mirrored) else None
        return None


def findRigNamespaces(data):
    """The namespaces in this scene that hold this rig - "" for no namespace.
    Checked against a handful of the rig's controls rather than all of them."""
    probes = (data.get("controls") or [])[:5]
    if not probes:
        return [""]
    candidates = [""] + (cmds.namespaceInfo(":", listOnlyNamespaces = True, recurse = True) or [])
    found = []
    for namespace in candidates:
        namespace = namespace.strip(":")
        if namespace in ("UI", "shared"):
            continue
        context = RigContext(data, namespace)
        if any(cmds.objExists(context.node(name)) for name in probes):
            found.append(namespace)
    return found


# ---------------------------------------------------------------- the ready-made actions

def defaultValue(node, attribute):
    try:
        default = cmds.attributeQuery(attribute, node = node, listDefault = True)
        return default[0] if default else None
    except Exception:
        return None


def animatableAttributes(node):
    return [attribute for attribute in (cmds.listAttr(node, keyable = True, unlocked = True, scalar = True) or [])
            if not cmds.listConnections("%s.%s" % (node, attribute), source = True, destination = False,
                                        skipConversionNodes = True)]


def resetControls(controls):
    for node in controls:
        for attribute in animatableAttributes(node):
            default = defaultValue(node, attribute)
            if default is not None:
                try:
                    cmds.setAttr("%s.%s" % (node, attribute), default)
                except Exception:
                    pass


def copyPose(source, target):
    for attribute in animatableAttributes(source):
        if cmds.attributeQuery(attribute, node = target, exists = True):
            try:
                cmds.setAttr("%s.%s" % (target, attribute), cmds.getAttr("%s.%s" % (source, attribute)))
            except Exception:
                pass


def runBuiltin(action_id, rig):
    """One of BUILTIN_ACTIONS. Returns a short message for the status line."""
    if action_id == "reset_rig":
        controls = rig.controls()
        resetControls(controls)
        return "Reset %d control(s)" % len(controls)
    if action_id == "reset_selected":
        controls = rig.selectedControls()
        resetControls(controls)
        return "Reset %d control(s)" % len(controls)
    if action_id == "select_all":
        controls = rig.controls()
        cmds.select(controls)
        return "Selected %d control(s)" % len(controls)
    if action_id == "select_mirror":
        mirrored = [m for m in (rig.mirrorName(node) for node in rig.selectedControls()) if m]
        cmds.select(mirrored) if mirrored else cmds.select(clear = True)
        return "Selected %d mirrored control(s)" % len(mirrored)
    if action_id in ("mirror_pose", "swap_pose"):
        pairs = [(node, rig.mirrorName(node)) for node in rig.selectedControls()]
        pairs = [(a, b) for a, b in pairs if b]
        if action_id == "mirror_pose":
            for source, target in pairs:
                copyPose(source, target)
        else:
            saved = {node: {a: cmds.getAttr("%s.%s" % (node, a)) for a in animatableAttributes(node)}
                     for pair in pairs for node in pair}
            for a, b in pairs:
                for source, target in ((a, b), (b, a)):
                    for attribute, value in saved[source].items():
                        if cmds.attributeQuery(attribute, node = target, exists = True):
                            try:
                                cmds.setAttr("%s.%s" % (target, attribute), value)
                            except Exception:
                                pass
        return "%s %d pair(s)" % ("Mirrored" if action_id == "mirror_pose" else "Swapped", len(pairs))
    if action_id == "key_selected":
        controls = rig.selectedControls()
        for node in controls:
            attributes = animatableAttributes(node)
            if attributes:
                cmds.setKeyframe(node, attribute = attributes)
        return "Keyed %d control(s)" % len(controls)
    raise ValueError("Unknown action '%s'" % action_id)


def runCode(code, rig, button_name = "button"):
    """A button's own Python, with rig, cmds and mel to hand."""
    namespace = {"rig": rig, "cmds": cmds, "mel": mel, "__name__": "picker_button"}
    exec(compile(code, "<picker: %s>" % button_name, "exec"), namespace)


def runAction(shape, rig, modifiers = None):
    """What a click on `shape` does - one undo step, errors caught.
    Returns (ok, message)."""
    action = shape.get("action") or {}
    kind = action.get("type", "none")
    if kind == "none":
        return True, ""
    cmds.undoInfo(openChunk = True, chunkName = "picker: %s" % shape.get("name", "button"))
    try:
        if kind == "select":
            names = [rig.node(name) for name in action.get("controls_resolved", [])]
            existing = [name for name in names if cmds.objExists(name)]
            shift = modifiers is not None and bool(modifiers & QtCore.Qt.ShiftModifier)
            ctrl = modifiers is not None and bool(modifiers & QtCore.Qt.ControlModifier)
            if not existing:
                return False, "None of this button's controls are in the scene"
            if ctrl:
                cmds.select(existing, toggle = True)
            elif shift:
                cmds.select(existing, add = True)
            else:
                cmds.select(existing, replace = True)
            missing = len(names) - len(existing)
            return True, "Selected %d control(s)%s" % (len(existing), " - %d missing" % missing if missing else "")
        if kind == "builtin":
            return True, runBuiltin(action.get("builtin", ""), rig)
        if kind == "code":
            runCode(action.get("code", ""), rig, shape.get("name", "button"))
            return True, "Ran '%s'" % shape.get("name", "button")
        return False, "Unknown action '%s'" % kind
    except Exception as error:
        traceback.print_exc()
        return False, "'%s' failed: %s: %s" % (shape.get("name", "button"), type(error).__name__, error)
    finally:
        cmds.undoInfo(closeChunk = True)


# ---------------------------------------------------------------- the window

class PickerCanvas(QtWidgets.QWidget):
    """The page, its shapes drawn exactly as in the editor, clickable."""

    def __init__(self, data, picker, parent = None):
        super().__init__(parent)
        self.data = data
        self.picker = picker
        page = data.get("page", {})
        self.setFixedSize(int(page.get("width", 400)), int(page.get("height", 600)))
        self.setMouseTracking(True)
        self.hovered = None
        self.pressed = None

    def shapes(self):
        return self.data.get("shapes", [])

    def actionableAt(self, point):
        """The topmost shape under the point that does something - a label on
        top of a button lets the click through to it."""
        for shape in reversed(self.shapes()):
            if (shape.get("action") or {}).get("type", "none") != "none" and shapeContains(shape, point):
                return shape
        return None

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), toColor(self.data.get("page", {}).get("background"), "#2B2B2B"))
        for shape in self.shapes():
            painter.save()
            painter.translate(shape.get("x", 0), shape.get("y", 0))
            highlight = 0.6 if shape is self.pressed else (0.3 if shape is self.hovered else 0.0)
            paintShape(painter, shape, highlight)
            painter.restore()
        painter.end()

    def eventPosition(self, event):
        return event.position() if QT6 else QtCore.QPointF(event.pos())

    def mouseMoveEvent(self, event):
        hovered = self.actionableAt(self.eventPosition(event))
        if hovered is not self.hovered:
            self.hovered = hovered
            self.setCursor(QtCore.Qt.PointingHandCursor if hovered else QtCore.Qt.ArrowCursor)
            self.setToolTip(self.picker.describe(hovered) if hovered else "")
            self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.pressed = self.actionableAt(self.eventPosition(event))
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.pressed is not None:
            shape = self.pressed
            self.pressed = None
            self.update()
            if shape is self.actionableAt(self.eventPosition(event)):
                self.picker.click(shape, event.modifiers())


class PickerWindow(QtWidgets.QWidget):

    def __init__(self, data, namespace = "", parent = None):
        super().__init__(parent)
        self.data = data
        self.rig = RigContext(data, namespace)
        self.setWindowTitle("%s Picker" % data.get("rig_name", "Rig"))
        self.setWindowFlags(QtCore.Qt.Window)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(QtWidgets.QLabel("Namespace:"))
        self.namespace_combo = QtWidgets.QComboBox()
        self.namespace_combo.setEditable(True)
        self.namespace_combo.setToolTip("The namespace the rig is referenced under - (none) for a rig "
                                        "opened directly")
        top.addWidget(self.namespace_combo, 1)
        refresh = QtWidgets.QPushButton("Refresh")
        refresh.clicked.connect(self.refreshNamespaces)
        top.addWidget(refresh)
        layout.addLayout(top)

        scroll = QtWidgets.QScrollArea()
        scroll.setAlignment(QtCore.Qt.AlignCenter)
        self.canvas = PickerCanvas(data, self)
        scroll.setWidget(self.canvas)
        layout.addWidget(scroll, 1)

        self.status = QtWidgets.QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.refreshNamespaces(namespace)
        self.namespace_combo.currentTextChanged.connect(self.onNamespaceChanged)
        page = data.get("page", {})
        self.resize(min(int(page.get("width", 400)) + 40, 1400), min(int(page.get("height", 600)) + 110, 1000))

    def refreshNamespaces(self, keep = None):
        current = keep if isinstance(keep, str) else self.rig.namespace
        found = findRigNamespaces(self.data) if cmds is not None else []
        self.namespace_combo.blockSignals(True)
        self.namespace_combo.clear()
        for namespace in found:
            self.namespace_combo.addItem(namespace or "(none)", namespace)
        index = self.namespace_combo.findData(current)
        if index < 0 and current:
            self.namespace_combo.addItem(current, current)
            index = self.namespace_combo.count() - 1
        self.namespace_combo.setCurrentIndex(max(index, 0))
        self.namespace_combo.blockSignals(False)
        self.onNamespaceChanged()

    def onNamespaceChanged(self, *args):
        index = self.namespace_combo.currentIndex()
        data = self.namespace_combo.itemData(index) if index >= 0 else None
        text = self.namespace_combo.currentText()
        namespace = data if data is not None and self.namespace_combo.itemText(index) == text else \
            ("" if text == "(none)" else text)
        self.rig = RigContext(self.data, namespace or "")

    def describe(self, shape):
        action = shape.get("action") or {}
        kind = action.get("type")
        if kind == "select":
            return "Select: " + ", ".join(action.get("controls_resolved", [])[:6]) + \
                   (" ..." if len(action.get("controls_resolved", [])) > 6 else "")
        if kind == "builtin":
            return BUILTIN_LABELS.get(action.get("builtin"), action.get("builtin", ""))
        if kind == "code":
            return shape.get("name") or "Script"
        return ""

    def click(self, shape, modifiers = None):
        ok, message = runAction(shape, self.rig, modifiers)
        self.status.setText(message)
        self.status.setStyleSheet("" if ok else "color: #E0A030;")
        return ok, message


def getMayaMainWindow():
    try:
        import maya.OpenMayaUI as omui #type: ignore
        try:
            from shiboken6 import wrapInstance #type: ignore
        except ImportError:
            from shiboken2 import wrapInstance #type: ignore
        pointer = omui.MQtUtil.mainWindow()
        return wrapInstance(int(pointer), QtWidgets.QWidget) if pointer else None
    except Exception:
        return None


def askNamespace(data, parent = None):
    """The namespace to drive. Asked whenever the scene does not settle it -
    several copies of the rig, or none found. Returns None when cancelled."""
    found = findRigNamespaces(data)
    if len(found) == 1:
        return found[0]
    dialog = QtWidgets.QInputDialog(parent)
    dialog.setWindowTitle("%s Picker" % data.get("rig_name", "Rig"))
    dialog.setLabelText("Which namespace is the rig in?" if found else
                        "No copy of the rig was found in the scene.\nType its namespace:")
    dialog.setComboBoxEditable(True)
    dialog.setComboBoxItems([namespace or "(none)" for namespace in found] or [""])
    if not dialog.exec():
        return None
    answer = dialog.textValue().strip()
    return "" if answer == "(none)" else answer


_open_pickers = []


def launch(data, namespace = None):
    """Open the picker. With namespace None the animator is asked."""
    parent = getMayaMainWindow()
    if namespace is None:
        namespace = askNamespace(data, parent)
        if namespace is None:
            return None
    window = PickerWindow(data, namespace, parent)
    window.show()
    #kept alive: a window without a reference is collected the moment this returns
    _open_pickers.append(window)
    return window
