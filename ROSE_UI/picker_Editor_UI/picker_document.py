"""The picker as data, and writing it out as the animator's script.

A document is plain JSON-able data, so the editor saves it with the project and
the exporter embeds it in the picker script unchanged:

    {"page":   {"width", "height", "background"},
     "shapes": [shape, ...]}                       - drawn in order, last on top

    shape = {"id", "name", "type": "rect" | "ellipse" | "polygon" | "text",
             "x", "y", "w", "h",                    - page pixels, top-left corner
             "radius",                              - a rectangle's corner rounding
             "points": [[x, y], ...],               - a polygon's, relative to x, y
             "contours": [[[x, y], ...], ...],      - instead of points: several outlines
             "fill_rule": "nonzero" | "evenodd",    - how overlapping outlines fill
             "fill":    {"enabled", "color"},
             "outline": {"enabled", "color", "width"},
             "text":    {"content", "size", "color", "align", "bold"},
             "opacity",
             "action":  {"type": "none" | "select" | "builtin" | "code",
                         "controls": [control id, ...], - for select
                         "builtin":  action id,          - see picker_runtime.BUILTIN_ACTIONS
                         "code":     python source}}

A button does exactly one of those things. Selection buttons hold control IDS,
not names - a renamed component keeps its picker - and the export turns them
into names ("controls_resolved"), without a namespace: the runtime adds the one
the animator picks.
"""

import copy
import json
import os
import uuid

DEFAULT_PAGE = {"width": 400, "height": 600, "background": "#2B2B2B"}
SHAPE_TYPES = ("rect", "ellipse", "polygon", "text")
ACTION_TYPES = ("none", "select", "builtin", "code")

DEFAULT_CODE = '''# rig.node("M_main_main_ctrl") is a rig object under the animator's namespace.
# cmds and mel are available; the whole click is one undo step.
selection = cmds.ls(selection = True)
'''

RUNTIME_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "picker_runtime.py")


def newDocument(width = DEFAULT_PAGE["width"], height = DEFAULT_PAGE["height"]):
    return {"page": dict(DEFAULT_PAGE, width = width, height = height), "shapes": []}


def newShape(kind, x, y, w, h, name = None):
    if kind not in SHAPE_TYPES:
        raise ValueError("unknown shape type '%s'" % kind)
    is_text = kind == "text"
    return {
        "id": uuid.uuid4().hex,
        "name": name or kind,
        "type": kind,
        "x": x, "y": y, "w": w, "h": h,
        "radius": 6 if kind == "rect" else 0,
        "points": [],
        #text is just text by default; any other shape a filled button
        "fill": {"enabled": not is_text, "color": "#4A90D9"},
        "outline": {"enabled": False, "color": "#101010", "width": 1.5},
        "text": {"content": "Text" if is_text else "", "size": 14, "color": "#FFFFFF", "align": "center",
                 "bold": False},
        "opacity": 1.0,
        "action": {"type": "none", "controls": [], "builtin": "reset_rig", "code": DEFAULT_CODE},
    }


def newPolygon(points, name = None):
    """A polygon from page points - stored relative to its bounding box."""
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    left, top = min(xs), min(ys)
    shape = newShape("polygon", left, top, max(max(xs) - left, 1), max(max(ys) - top, 1), name)
    shape["points"] = [[x - left, y - top] for x, y in points]
    return shape


def newContourPolygon(contours, fill_rule = "nonzero", name = None):
    """A polygon of several outlines, from page points - holes, separate parts."""
    points = [point for contour in contours for point in contour]
    shape = newPolygon(points, name)
    left, top = shape["x"], shape["y"]
    shape["points"] = []
    shape["contours"] = [[[x - left, y - top] for x, y in contour] for contour in contours]
    shape["fill_rule"] = fill_rule
    return shape


def resizeShape(shape, x, y, w, h):
    """Move and size a shape; a polygon's points scale with its box."""
    w, h = max(w, 1), max(h, 1)
    if shape["type"] == "polygon":
        scale_x, scale_y = w / float(max(shape["w"], 1e-6)), h / float(max(shape["h"], 1e-6))
        if shape.get("points"):
            shape["points"] = [[px * scale_x, py * scale_y] for px, py in shape["points"]]
        if shape.get("contours"):
            shape["contours"] = [[[px * scale_x, py * scale_y] for px, py in contour] for contour in shape["contours"]]
    shape.update(x = x, y = y, w = w, h = h)


def duplicateShape(shape, offset = 10):
    clone = copy.deepcopy(shape)
    clone["id"] = uuid.uuid4().hex
    clone["x"] += offset
    clone["y"] += offset
    clone["name"] = shape.get("name", "shape") + "_copy"
    return clone


def resolveDocument(document, control_names, all_controls, rig_name, mirror_prefixes):
    """The data the picker script runs on: the document, with each selection
    button's control ids turned into names. Returns (data, [problems])."""
    data = copy.deepcopy(document)
    problems = []
    for shape in data.get("shapes", []):
        action = shape.get("action") or {}
        if action.get("type") == "select":
            resolved = []
            for control_id in action.get("controls", []):
                name = control_names.get(str(control_id))
                if name is None:
                    problems.append("'%s' selects a control that is no longer in the rig" % shape.get("name"))
                else:
                    resolved.append(name)
            action["controls_resolved"] = resolved
            if not resolved:
                problems.append("'%s' selects nothing" % shape.get("name"))
        #only what the button does travels - an unused code block or action is noise
        kept = {"select": "controls", "builtin": "builtin", "code": "code"}.get(action.get("type"))
        for key in ("controls", "builtin", "code"):
            if key != kept:
                action.pop(key, None)
    data["controls"] = list(all_controls)
    data["rig_name"] = rig_name
    data["mirror_prefixes"] = [list(pair) for pair in mirror_prefixes]
    data["version"] = 1
    return data, problems


def writePickerScript(data, path):
    """The animator's script: the runtime, the picker's data, and the call that
    opens it. Self-contained - Maya and Qt are all it needs."""
    with open(RUNTIME_PATH, "r") as source:
        runtime = source.read()
    header = ('# %s rig picker - written by ROSE. Run it in the Script Editor, or put it on a shelf:\n'
              '#     exec(open(r"%s").read())\n'
              '# It asks for the rig\'s namespace, then opens the picker.\n\n') % (data.get("rig_name", "Rig"), path)
    payload = json.dumps(data, indent = 1)
    with open(path, "w") as script:
        script.write(header)
        script.write(runtime)
        script.write("\n\n# ---------------------------------------------------------------- this rig's picker\n\n")
        script.write("PICKER_DATA = json.loads(%r)\n\n" % payload)
        script.write("if __name__ == '__main__':\n    launch(PICKER_DATA)\n")
    return path
