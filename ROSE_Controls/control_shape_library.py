"""The control shape libraries, and which shape each control gets.

Two halves with different lifetimes:

The LIBRARIES hold the shapes. There is one GENERAL library, shared by every
project, next to this module; and each node pack can carry a RIG library of its
own, in a control_shape_library/ folder beside its rose_pack.json, for shapes that
only make sense for that rig and should travel with its repo. Both look the same
inside: one .mb per shape and library.json holding each shape's file and its
preview. Shapes are stored normalised to fit a unit box (-0.5..0.5 on every
axis, the size the default control shapes are drawn at), so any shape comes out
the same size as a default one at the same control size.

A library is named by an id - GENERAL_LIBRARY_ID, or a pack's pack_id - never by
its folder: a pack sits at a different path on every machine, its id does not.

The ASSIGNMENTS belong to a project and are owned by the Control Shapes tab,
which pushes them in here. They are kept at module level on purpose: a control
is drawn from inside a component build, which can be started from the ROSE
editor, the pipeline or a context menu, and none of those know about the tab.
Every one of them reads this registry instead.

Whether shapes apply at all is asked of an "enabled provider" - the editor
points it at the pipeline, so disabling the Control Shapes step there turns them
off for every build.
"""

import json
import os
import re

import maya.cmds as cmds #type: ignore
import maya.api.OpenMaya as om #type: ignore

from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

GENERAL_LIBRARY_ID = "general"
#the folder name, both next to this module and inside a node pack
LIBRARY_FOLDER_NAME = "control_shape_library"
LIBRARY_FILE_NAME = "library.json"
GENERAL_LIBRARY_DIRECTORY = os.path.join(os.path.dirname(__file__), LIBRARY_FOLDER_NAME)
LIBRARY_VERSION = 1

#half the unit box: the largest distance any point of a stored shape reaches from
#the control's pivot on any axis - what the default circle is drawn at
NORMALIZED_EXTENT = 0.5
#points sampled along each curve for the preview, and to measure the size by. The
#curve rather than its CVs: a smooth curve's CVs sit well outside it
PREVIEW_SAMPLES = 48

IMPORT_NAMESPACE = "roseShapeImport"
SHAPE_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


# Where libraries are

def getLibraryDirectory(library_id):
    """The folder a library lives in, or None for a rig library whose pack is not
    loaded on this machine."""
    if not library_id or library_id == GENERAL_LIBRARY_ID:
        return GENERAL_LIBRARY_DIRECTORY

    #imported here, not at the top: the pack loader imports every node module,
    #and they import this one through control.py - a circular import at load time
    from MNRB.ROSE_Packs.pack_loader import LOADED_PACKS #type: ignore
    pack = LOADED_PACKS.get(library_id)
    return os.path.join(pack["path"], LIBRARY_FOLDER_NAME) if pack else None


def getLibraryLabel(library_id):
    if not library_id or library_id == GENERAL_LIBRARY_ID:
        return "General"

    from MNRB.ROSE_Packs.pack_loader import LOADED_PACKS #type: ignore
    pack = LOADED_PACKS.get(library_id)
    return "%s (rig)" % (pack["label"] if pack else library_id)


def getRigLibraryIds(type_ids):
    """The rig libraries a graph made of these node types can use - one per
    loaded node pack it draws components from."""
    from MNRB.ROSE_Packs.pack_loader import LOADED_PACKS #type: ignore
    pack_ids = []
    for type_id in type_ids:
        pack_id = str(type_id).split(".")[0]
        if pack_id in LOADED_PACKS and pack_id not in pack_ids:
            pack_ids.append(pack_id)
    return pack_ids


# Library contents

def loadLibrary(library_id = GENERAL_LIBRARY_ID):
    """{"shapes": {name: {"file": ..., "preview": [[[x, y, z], ...], ...]}}}"""
    empty = {"version": LIBRARY_VERSION, "shapes": {}}
    directory = getLibraryDirectory(library_id)
    if directory is None:
        return empty

    library_file = os.path.join(directory, LIBRARY_FILE_NAME)
    if not os.path.isfile(library_file):
        return empty
    try:
        with open(library_file, "r") as file:
            data = json.load(file)
    except (OSError, ValueError) as error:
        log.error("CONTROLSHAPELIBRARY:: --loadLibrary:: could not read '%s': %s" % (library_file, error))
        return empty
    data.setdefault("shapes", {})
    return data


def saveLibrary(library, library_id = GENERAL_LIBRARY_ID):
    directory = getLibraryDirectory(library_id)
    os.makedirs(directory, exist_ok = True)
    with open(os.path.join(directory, LIBRARY_FILE_NAME), "w") as file:
        json.dump(library, file, indent = 4)


def getShapeNames(library_id = GENERAL_LIBRARY_ID):
    return sorted(loadLibrary(library_id)["shapes"].keys(), key = str.lower)


def getShapeFile(shape_name, library_id = GENERAL_LIBRARY_ID):
    """The shape's .mb path, or None if it is not in the library or its file is gone."""
    entry = loadLibrary(library_id)["shapes"].get(shape_name)
    if entry is None:
        return None
    path = os.path.join(getLibraryDirectory(library_id), entry["file"])
    return path if os.path.isfile(path) else None


def getShapePreview(shape_name, library_id = GENERAL_LIBRARY_ID):
    entry = loadLibrary(library_id)["shapes"].get(shape_name)
    return entry.get("preview", []) if entry else []


def isValidShapeName(shape_name):
    return bool(SHAPE_NAME_PATTERN.match(shape_name or ""))


def addShapeFromSelection(shape_name, library_id = GENERAL_LIBRARY_ID, overwrite = False):
    """Store the selected curve transform in a library as shape_name.

    The shape is taken as it looks in the viewport, with the object moved to
    world zero - its pivot on the origin, so the pivot becomes the control's
    origin and a shape drawn off to one side of it (a cog handle in front of the
    wheel, say) keeps that offset - and scaled to the unit box. Returns
    (success, message).
    """
    if not isValidShapeName(shape_name):
        return False, "'%s' is not a valid name - letters, digits and underscores, starting with a letter" % shape_name

    library_directory = getLibraryDirectory(library_id)
    if library_directory is None:
        return False, "The node pack '%s' is not loaded, so its rig library cannot be written to" % library_id

    library = loadLibrary(library_id)
    if shape_name in library["shapes"] and not overwrite:
        return False, "A shape called '%s' already exists in the %s library" % (shape_name, getLibraryLabel(library_id))

    selection = cmds.ls(selection = True, type = "transform", long = True) or []
    if len(selection) != 1:
        return False, "Select exactly one curve object"
    source = selection[0]
    source_shapes = cmds.listRelatives(source, shapes = True, type = "nurbsCurve",
                                       fullPath = True, noIntermediate = True) or []
    if not source_shapes:
        return False, "'%s' has no NURBS curve shapes" % source

    #The object's position becomes the control's origin: its pivot, in world
    #space, goes to world zero. xform reports it with every parent and the
    #offsetParentMatrix already applied.
    pivot = om.MVector(*cmds.xform(source, query = True, worldSpace = True, rotatePivot = True))

    #Built into a brand new transform rather than a duplicate of the source.
    #A duplicate carries everything its transform had - an offsetParentMatrix
    #above all, which Freeze Transformations does not bake - and that stayed
    #in the stored file: the shape's points were stored relative to a frame
    #that the control's own constraint then replaced, which put the shape
    #wherever that frame had been, typically at the world origin. Locked
    #channels made freezing fail outright. Reading each curve's points in
    #world space and writing them into a clean transform sidesteps all of it,
    #and leaves the artist's curve untouched.
    clean = cmds.createNode("transform", name = shape_name, skipSelect = True)
    try:
        clean_object = om.MSelectionList().add(clean).getDependNode(0)
        for source_shape in source_shapes:
            source_curve = om.MFnNurbsCurve(om.MSelectionList().add(source_shape).getDagPath(0))
            world_points = source_curve.cvPositions(om.MSpace.kWorld)

            new_curve = om.MFnNurbsCurve(om.MFnNurbsCurve().copy(source_curve.object(), clean_object))
            new_curve.setCVPositions([point - pivot for point in world_points], om.MSpace.kObject)
            new_curve.updateCurve()

        renameShapesAfter(clean)
        curve_shapes = cmds.listRelatives(clean, shapes = True, type = "nurbsCurve", fullPath = True)

        extent = max((abs(coordinate) for polyline in sampleCurves(curve_shapes)
                      for point in polyline for coordinate in point), default = 0.0)
        if extent < 1e-6:
            return False, "'%s' has no size to normalise" % source
        factor = NORMALIZED_EXTENT / extent
        for curve_shape in curve_shapes:
            cmds.scale(factor, factor, factor, curve_shape + ".cv[*]", pivot = (0, 0, 0), relative = True)

        preview = [[[round(value, 4) for value in point] for point in polyline]
                   for polyline in sampleCurves(curve_shapes)]

        os.makedirs(library_directory, exist_ok = True)
        file_name = shape_name + ".mb"
        cmds.select(clean, replace = True)
        cmds.file(os.path.join(library_directory, file_name), exportSelected = True, type = "mayaBinary",
                  force = True, constructionHistory = False, channels = False,
                  expressions = False, constraints = False, shader = False)
    finally:
        if cmds.objExists(clean):
            cmds.delete(clean)
        cmds.select(source, replace = True)

    library["shapes"][shape_name] = {"file": file_name, "preview": preview}
    saveLibrary(library, library_id)
    return True, "Stored '%s' in the %s library" % (shape_name, getLibraryLabel(library_id))


def removeShape(shape_name, library_id = GENERAL_LIBRARY_ID):
    library_directory = getLibraryDirectory(library_id)
    if library_directory is None:
        return False, "The node pack '%s' is not loaded" % library_id

    library = loadLibrary(library_id)
    entry = library["shapes"].pop(shape_name, None)
    if entry is None:
        return False, "No shape called '%s' in the %s library" % (shape_name, getLibraryLabel(library_id))

    path = os.path.join(library_directory, entry["file"])
    if os.path.isfile(path):
        os.remove(path)
    saveLibrary(library, library_id)
    return True, "Removed '%s' from the %s library" % (shape_name, getLibraryLabel(library_id))


def sampleCurves(curve_shapes):
    """Points along each curve in its object space - one polyline per curve.

    A degree 1 curve is exactly its CVs; anything smoother is sampled evenly
    across its parameter range, closed ones back round to the start."""
    polylines = []
    for curve_shape in curve_shapes:
        curve = om.MFnNurbsCurve(om.MSelectionList().add(curve_shape).getDagPath(0))

        if curve.degree == 1:
            points = [curve.cvPosition(index) for index in range(curve.numCVs)]
            if curve.form != om.MFnNurbsCurve.kOpen:
                points.append(points[0])
        else:
            start, end = curve.knotDomain
            count = PREVIEW_SAMPLES
            points = [curve.getPointAtParam(start + (end - start) * index / count)
                      for index in range(count + 1)]

        polylines.append([(point.x, point.y, point.z) for point in points])
    return polylines


# Assignments - pushed in by the Control Shapes tab

_assignments = {}
_enabled_provider = None


def setAssignments(assignments):
    """{str(control id): {"shape": name or None, "library": library id, "scale": float}}

    An assignment without "library" is from the general library - what every
    assignment was before rig libraries existed."""
    global _assignments
    _assignments = dict(assignments)


def setEnabledProvider(provider):
    """A callable answering whether library shapes should be used right now."""
    global _enabled_provider
    _enabled_provider = provider


def isEnabled():
    if _enabled_provider is None:
        return True
    try:
        return bool(_enabled_provider())
    except Exception as error:
        #a broken provider should not stop a rig from building
        log.warning("CONTROLSHAPELIBRARY:: --isEnabled:: enabled check failed, using shapes: %s" % error)
        return True


def resolveControlShape(control_id):
    """(library file or None, scale multiplier) for a control.

    None as the file means "draw the default shape". The scale override applies
    either way, so a control can be resized without a custom shape.
    """
    if not isEnabled():
        return None, 1.0

    assignment = _assignments.get(str(control_id))
    if not assignment:
        return None, 1.0

    scale = float(assignment.get("scale", 1.0))
    shape_name = assignment.get("shape")
    if not shape_name:
        return None, scale

    library_id = assignment.get("library") or GENERAL_LIBRARY_ID
    path = getShapeFile(shape_name, library_id)
    if path is None:
        log.warning("CONTROLSHAPELIBRARY:: --resolveControlShape:: shape '%s' is not in the %s library, "
                    "using the default shape" % (shape_name, getLibraryLabel(library_id)))
        return None, scale
    return path, scale


# Drawing

def importShape(path, name):
    """Import a shape file into a fresh transform called name, and return it.

    Only the file's curve SHAPES are used, moved under a transform created here.
    The file's own transform is thrown away with everything it carries - an
    offsetParentMatrix, locked or non-zero channels, pivots, inheritsTransform -
    any of which would otherwise become the control's, and move it off the
    place the component puts it.
    """
    cmds.file(path, i = True, type = "mayaBinary", mergeNamespacesOnClash = False,
              namespace = IMPORT_NAMESPACE)

    curve_objects = [transform for transform in
                     (cmds.ls(IMPORT_NAMESPACE + ":*", type = "transform", long = True) or [])
                     if cmds.listRelatives(transform, shapes = True, type = "nurbsCurve", noIntermediate = True)]

    #created in the root namespace, not the import one, so it survives the
    #namespace being cleared below
    control_transform = None
    if curve_objects:
        control_transform = cmds.createNode("transform", name = ":" + name, skipSelect = True)

        source_shapes = cmds.listRelatives(curve_objects[0], shapes = True, type = "nurbsCurve",
                                           fullPath = True, noIntermediate = True)
        #baked first: a curve still driven by construction history (a makeNurbCircle,
        #say) is left empty once that node is deleted with the rest below
        cmds.delete(source_shapes, constructionHistory = True)
        for source_shape in source_shapes:
            #relative: the shape keeps its own points and ignores the transform it
            #came from - that transform's offsets are exactly what is being dropped
            cmds.parent(source_shape, control_transform, shape = True, relative = True)
        #out of the import namespace BEFORE it is cleared below, or the clearing
        #would delete the very shapes just moved over
        renameShapesAfter(control_transform)

    #everything the file brought, its transform included, goes
    for node in cmds.ls(IMPORT_NAMESPACE + ":*", long = True) or []:
        if cmds.objExists(node):
            cmds.delete(node)
    cmds.namespace(removeNamespace = IMPORT_NAMESPACE, mergeNamespaceWithRoot = True)

    if control_transform is None:
        raise RuntimeError("'%s' holds no curve object" % path)
    return control_transform


def renameShapesAfter(transform):
    """Name a transform's shapes after it. Shapes keep whatever they were saved
    as otherwise, which clashes with any other object that was stored the same
    way - and a clashing short name makes every later call on it ambiguous."""
    short_name = transform.split("|")[-1].split(":")[-1]
    shapes = cmds.listRelatives(transform, shapes = True, fullPath = True) or []
    for index, shape in enumerate(shapes):
        #":" puts it in the root namespace - a shape imported into a temporary
        #namespace would otherwise stay in it, and go when that is cleared
        cmds.rename(shape, ":%sShape%s" % (short_name, index if index else ""))


def replaceControlShapes(control_transform, path, size):
    """Swap the curves under an existing control for the ones in path, at size.

    The control transform is untouched - its position, channels, connections and
    attributes stay - only its shape nodes are exchanged."""
    temporary = importShape(path, control_transform + "_shapeSwap")
    try:
        cmds.scale(size, size, size, temporary, relative = True)
        cmds.makeIdentity(temporary, apply = True, scale = True)

        old_shapes = cmds.listRelatives(control_transform, shapes = True, fullPath = True) or []
        if old_shapes:
            cmds.delete(old_shapes)

        for new_shape in cmds.listRelatives(temporary, shapes = True, fullPath = True) or []:
            cmds.parent(new_shape, control_transform, shape = True, relative = True)
        renameShapesAfter(control_transform)
    finally:
        if cmds.objExists(temporary):
            cmds.delete(temporary)
