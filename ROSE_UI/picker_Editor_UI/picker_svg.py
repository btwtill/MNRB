"""SVG files as picker shapes.

The picker draws rectangles, ellipses, polygons (several outlines, with SVG's
fill rules) and text. An SVG maps onto those like this:

    rect, circle, ellipse   kept as themselves while only moved and scaled;
                            turned or sheared, they become polygons
    polygon, polyline, path polygons - curves and arcs sampled into points, every
                            subpath an outline of one shape, so holes stay holes
    line, open paths with   the outline turned into a filled shape: the picker
      only a stroke         only outlines closed shapes
    text, tspan             text
    g, svg, a, use          what they hold, with their transforms
    image, filters, masks,  skipped, and counted in the warnings
      clip paths

Styles come from attributes and style="...", inherited down groups. A
gradient fill becomes its first colour. Transforms (matrix, translate, scale,
rotate, skewX, skewY) and the viewBox are applied to the geometry itself.

importSvg() returns the shapes in page pixels, fitted onto the page when the
drawing is larger than it.
"""

import math
import re
import xml.etree.ElementTree as ElementTree

from PySide6 import QtCore, QtGui #type: ignore

from MNRB.ROSE_UI.picker_Editor_UI import picker_document as document_model #type: ignore

#a margin left round a drawing fitted onto the page
FIT_MARGIN = 10.0
UNITS = {"px": 1.0, "pt": 4.0 / 3.0, "pc": 16.0, "mm": 96.0 / 25.4, "cm": 96.0 / 2.54, "in": 96.0, "": 1.0}
NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
PATH_TOKEN = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
INHERITED = ("fill", "stroke", "stroke-width", "fill-opacity", "stroke-opacity", "fill-rule", "font-size",
             "font-weight", "text-anchor", "visibility", "color")
SKIPPED = {"defs", "clipPath", "mask", "symbol", "marker", "pattern", "linearGradient", "radialGradient",
           "metadata", "title", "desc", "style", "script", "filter"}


# ---------------------------------------------------------------- geometry helpers

class Matrix:
    """An SVG affine transform: (a c e / b d f)."""

    def __init__(self, a = 1.0, b = 0.0, c = 0.0, d = 1.0, e = 0.0, f = 0.0):
        self.a, self.b, self.c, self.d, self.e, self.f = a, b, c, d, e, f

    def __mul__(self, other):
        return Matrix(self.a * other.a + self.c * other.b, self.b * other.a + self.d * other.b,
                      self.a * other.c + self.c * other.d, self.b * other.c + self.d * other.d,
                      self.a * other.e + self.c * other.f + self.e, self.b * other.e + self.d * other.f + self.f)

    def apply(self, x, y):
        return (self.a * x + self.c * y + self.e, self.b * x + self.d * y + self.f)

    def scale(self):
        """The average scale - what a stroke width or font size changes by."""
        return math.sqrt(abs(self.a * self.d - self.b * self.c)) or 1.0

    def isAxisAligned(self):
        return abs(self.b) < 1e-9 and abs(self.c) < 1e-9


def parseTransform(text):
    matrix = Matrix()
    for name, arguments in re.findall(r"(\w+)\s*\(([^)]*)\)", text or ""):
        values = [float(v) for v in NUMBER.findall(arguments)]
        if name == "matrix" and len(values) == 6:
            step = Matrix(*values)
        elif name == "translate":
            step = Matrix(e = values[0], f = values[1] if len(values) > 1 else 0.0)
        elif name == "scale":
            step = Matrix(a = values[0], d = values[1] if len(values) > 1 else values[0])
        elif name == "rotate":
            angle = math.radians(values[0])
            rotation = Matrix(math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle))
            if len(values) == 3:
                cx, cy = values[1], values[2]
                rotation = Matrix(e = cx, f = cy) * rotation * Matrix(e = -cx, f = -cy)
            step = rotation
        elif name == "skewX":
            step = Matrix(c = math.tan(math.radians(values[0])))
        elif name == "skewY":
            step = Matrix(b = math.tan(math.radians(values[0])))
        else:
            continue
        matrix = matrix * step
    return matrix


def length(text, default = 0.0, relative_to = None):
    if text is None:
        return default
    match = re.match(r"\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)\s*(px|pt|pc|mm|cm|in|%)?", str(text))
    if not match:
        return default
    value, unit = float(match.group(1)), match.group(2) or ""
    if unit == "%":
        return value / 100.0 * (relative_to if relative_to is not None else 100.0)
    return value * UNITS.get(unit, 1.0)


def samplesFor(points):
    """How many points to sample a curve with - by how long its control polygon is."""
    span = sum(math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))
    return max(4, min(64, int(math.ceil(math.sqrt(span) * 2.0))))


def cubic(p0, p1, p2, p3):
    count = samplesFor([p0, p1, p2, p3])
    result = []
    for step in range(1, count + 1):
        t = step / float(count)
        u = 1.0 - t
        result.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                       u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return result


def arcPoints(start, rx, ry, rotation, large_arc, sweep, end):
    """An SVG elliptical arc as points in its own (untransformed) space - the
    endpoint-to-centre conversion of the SVG implementation notes."""
    x1, y1 = start
    x2, y2 = end
    if (x1, y1) == (x2, y2):
        return []
    rx, ry = abs(rx), abs(ry)
    if rx < 1e-9 or ry < 1e-9:
        return [end]
    phi = math.radians(rotation)
    cos_phi, sin_phi = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p, y1p = cos_phi * dx + sin_phi * dy, -sin_phi * dx + cos_phi * dy
    radii = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if radii > 1:
        rx, ry = rx * math.sqrt(radii), ry * math.sqrt(radii)
    numerator = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    denominator = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    factor = math.sqrt(max(numerator / denominator, 0.0)) if denominator else 0.0
    if large_arc == sweep:
        factor = -factor
    cxp, cyp = factor * rx * y1p / ry, -factor * ry * x1p / rx
    cx = cos_phi * cxp - sin_phi * cyp + (x1 + x2) / 2.0
    cy = sin_phi * cxp + cos_phi * cyp + (y1 + y2) / 2.0

    def angle(ux, uy, vx, vy):
        value = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return value
    theta1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    delta = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and delta > 0:
        delta -= 2 * math.pi
    elif sweep and delta < 0:
        delta += 2 * math.pi
    count = max(4, int(abs(delta) / (2 * math.pi) * 64))
    points = []
    for step in range(1, count + 1):
        t = theta1 + delta * step / float(count)
        points.append((cx + rx * math.cos(t) * cos_phi - ry * math.sin(t) * sin_phi,
                       cy + rx * math.cos(t) * sin_phi + ry * math.sin(t) * cos_phi))
    return points


def parsePath(d, matrix):
    """[(points, closed)] - each subpath of `d`, transformed, curves sampled.
    Bezier control points are transformed before sampling (a curve's transform
    is its control points' transform); arcs are sampled first, then transformed."""
    tokens = PATH_TOKEN.findall(d or "")
    subpaths = []
    points = []
    current = start = (0.0, 0.0)
    last_control = None
    previous_command = ""
    index = 0
    command = None

    def number():
        nonlocal index
        value = float(tokens[index])
        index += 1
        return value

    def flush(closed):
        nonlocal points
        if len(points) > 1:
            subpaths.append((points, closed))
        points = []

    while index < len(tokens):
        if re.match(r"[A-Za-z]", tokens[index]):
            command = tokens[index]
            index += 1
        elif command is None:
            index += 1
            continue
        relative = command.islower()
        kind = command.upper()
        try:
            if kind == "Z":
                if points:
                    flush(True)
                current = start
                last_control = None
                previous_command = command
                #Z takes no numbers - a following number restarts with a moveto
                command = None
                continue
            if kind == "M":
                x, y = number(), number()
                if relative:
                    x, y = current[0] + x, current[1] + y
                flush(False)
                current = start = (x, y)
                points = [matrix.apply(x, y)]
                #further pairs after a moveto are linetos
                command = "l" if relative else "L"
                last_control = None
            elif kind in ("L", "H", "V"):
                if kind == "L":
                    x, y = number(), number()
                    if relative:
                        x, y = current[0] + x, current[1] + y
                elif kind == "H":
                    x = number() + (current[0] if relative else 0.0)
                    y = current[1]
                else:
                    x = current[0]
                    y = number() + (current[1] if relative else 0.0)
                current = (x, y)
                points.append(matrix.apply(x, y))
                last_control = None
            elif kind in ("C", "S"):
                if kind == "C":
                    c1 = (number(), number())
                    if relative:
                        c1 = (current[0] + c1[0], current[1] + c1[1])
                else:
                    c1 = (2 * current[0] - last_control[0], 2 * current[1] - last_control[1]) \
                        if previous_command.upper() in ("C", "S") and last_control else current
                c2, end = (number(), number()), (number(), number())
                if relative:
                    c2 = (current[0] + c2[0], current[1] + c2[1])
                    end = (current[0] + end[0], current[1] + end[1])
                points += cubic(matrix.apply(*current), matrix.apply(*c1), matrix.apply(*c2), matrix.apply(*end))
                last_control, current = c2, end
            elif kind in ("Q", "T"):
                if kind == "Q":
                    control = (number(), number())
                    if relative:
                        control = (current[0] + control[0], current[1] + control[1])
                else:
                    control = (2 * current[0] - last_control[0], 2 * current[1] - last_control[1]) \
                        if previous_command.upper() in ("Q", "T") and last_control else current
                end = (number(), number())
                if relative:
                    end = (current[0] + end[0], current[1] + end[1])
                #a quadratic as the cubic it is
                c1 = (current[0] + 2.0 / 3.0 * (control[0] - current[0]), current[1] + 2.0 / 3.0 * (control[1] - current[1]))
                c2 = (end[0] + 2.0 / 3.0 * (control[0] - end[0]), end[1] + 2.0 / 3.0 * (control[1] - end[1]))
                points += cubic(matrix.apply(*current), matrix.apply(*c1), matrix.apply(*c2), matrix.apply(*end))
                last_control, current = control, end
            elif kind == "A":
                rx, ry, rotation = number(), number(), number()
                large_arc, sweep = int(number()), int(number())
                end = (number(), number())
                if relative:
                    end = (current[0] + end[0], current[1] + end[1])
                points += [matrix.apply(*p) for p in arcPoints(current, rx, ry, rotation, large_arc, sweep, end)]
                current = end
                last_control = None
            if not points:
                points = [matrix.apply(*current)]
            previous_command = command
        except (IndexError, ValueError):
            break
    flush(False)
    return [(cleanPoints(p), closed) for p, closed in subpaths if len(cleanPoints(p)) > 1]


def cleanPoints(points):
    """Without repeated points, and without a last point that only closes the loop."""
    cleaned = []
    for point in points:
        if not cleaned or math.dist(cleaned[-1], point) > 1e-6:
            cleaned.append(point)
    if len(cleaned) > 2 and math.dist(cleaned[0], cleaned[-1]) < 1e-6:
        cleaned.pop()
    return cleaned


def ellipsePoints(cx, cy, rx, ry, matrix, count = 48):
    return [matrix.apply(cx + rx * math.cos(2 * math.pi * i / count), cy + ry * math.sin(2 * math.pi * i / count))
            for i in range(count)]


def roundedRectPoints(x, y, w, h, rx, ry, matrix):
    if rx <= 0 or ry <= 0:
        return [matrix.apply(*p) for p in ((x, y), (x + w, y), (x + w, y + h), (x, y + h))]
    points = []
    for corner_x, corner_y, start in ((x + w - rx, y + ry, -90), (x + w - rx, y + h - ry, 0),
                                      (x + rx, y + h - ry, 90), (x + rx, y + ry, 180)):
        for step in range(9):
            angle = math.radians(start + step * 90 / 8.0)
            points.append(matrix.apply(corner_x + rx * math.cos(angle), corner_y + ry * math.sin(angle)))
    return points


# ---------------------------------------------------------------- styles

def parseStyle(element, inherited):
    style = {key: value for key, value in inherited.items() if key in INHERITED}
    for key in INHERITED + ("opacity", "display"):
        if element.get(key) is not None:
            style[key] = element.get(key).strip()
    for declaration in (element.get("style") or "").split(";"):
        if ":" in declaration:
            key, value = declaration.split(":", 1)
            style[key.strip()] = value.strip()
    return style


class SvgImporter:

    def __init__(self, page_width, page_height):
        self.page_width, self.page_height = page_width, page_height
        self.shapes = []
        self.warnings = []
        self.ids = {}
        self.gradient_colors = {}
        self.counts = {}

    def colorFor(self, value, style, opacity):
        """(enabled, "#AARRGGBB") for a fill or stroke value."""
        if value is None or value == "none" or value == "transparent":
            return False, "#000000"
        if value.startswith("url("):
            reference = value[value.find("#") + 1:value.find(")")].strip()
            value = self.gradient_colors.get(reference)
            if value is None:
                return False, "#000000"
        if value == "currentColor":
            value = style.get("color", "#000000")
        match = re.match(r"rgba?\(([^)]*)\)", value)
        if match:
            parts = [p.strip() for p in match.group(1).split(",")]
            channels = [int(round(float(p[:-1]) * 2.55)) if p.endswith("%") else int(round(float(p))) for p in parts[:3]]
            color = QtGui.QColor(*channels)
            if len(parts) > 3:
                opacity *= float(parts[3])
        else:
            color = QtGui.QColor(value)
        if not color.isValid():
            self.warn("colour '%s' not understood - grey used" % value)
            color = QtGui.QColor("#808080")
        color.setAlphaF(max(0.0, min(1.0, opacity)))
        return True, color.name(QtGui.QColor.HexArgb) if color.alpha() < 255 else color.name()

    def warn(self, message):
        if message not in self.warnings:
            self.warnings.append(message)

    def nameFor(self, element, tag):
        if element.get("id"):
            return element.get("id")
        self.counts[tag] = self.counts.get(tag, 0) + 1
        return "%s%d" % (tag, self.counts[tag])

    # -- reading

    def read(self, root):
        for element in root.iter():
            element.tag = element.tag.split("}")[-1]
            if element.get("id"):
                self.ids[element.get("id")] = element
            for key in list(element.attrib):
                if "}" in key:
                    element.attrib[key.split("}")[-1]] = element.attrib.pop(key)
        for gradient in [e for e in root.iter() if e.tag in ("linearGradient", "radialGradient")]:
            stops = [e for e in gradient.iter() if e.tag == "stop"]
            if not stops and gradient.get("href", "").startswith("#"):
                linked = self.ids.get(gradient.get("href")[1:])
                stops = [e for e in linked.iter() if e.tag == "stop"] if linked is not None else []
            if stops:
                #stop-color is not one of the inherited properties parseStyle reads,
                #so it is looked up here - attribute or style declaration
                declared = dict(d.split(":", 1) for d in (stops[0].get("style") or "").split(";") if ":" in d)
                declared = {key.strip(): value.strip() for key, value in declared.items()}
                self.gradient_colors[gradient.get("id")] = declared.get("stop-color", stops[0].get("stop-color", "#808080"))
                self.warn("gradients are filled with their first colour")
        self.walk(root, self.rootMatrix(root), {"fill": "black"})

    def rootMatrix(self, root):
        view_box = [float(v) for v in NUMBER.findall(root.get("viewBox") or "")]
        if len(view_box) != 4 or view_box[2] <= 0 or view_box[3] <= 0:
            return Matrix()
        width = length(root.get("width"), view_box[2])
        height = length(root.get("height"), view_box[3])
        scale_x, scale_y = width / view_box[2], height / view_box[3]
        if (root.get("preserveAspectRatio") or "").strip() == "none":
            return Matrix(a = scale_x, d = scale_y, e = -view_box[0] * scale_x, f = -view_box[1] * scale_y)
        scale = min(scale_x, scale_y)
        offset_x = (width - view_box[2] * scale) / 2.0
        offset_y = (height - view_box[3] * scale) / 2.0
        return Matrix(a = scale, d = scale, e = offset_x - view_box[0] * scale, f = offset_y - view_box[1] * scale)

    def walk(self, element, matrix, inherited):
        for child in element:
            if child.tag in SKIPPED:
                continue
            style = parseStyle(child, inherited)
            if style.get("display") == "none":
                continue
            child_matrix = matrix * parseTransform(child.get("transform"))
            #opacity multiplies down groups rather than being inherited as is
            style["group-opacity"] = float(inherited.get("group-opacity", 1.0)) * float(style.get("opacity", 1.0))
            style.pop("opacity", None)
            tag = child.tag
            if tag in ("g", "a", "switch"):
                self.walk(child, child_matrix, style)
            elif tag == "svg":
                nested = Matrix(e = length(child.get("x")), f = length(child.get("y"))) * self.rootMatrix(child)
                self.walk(child, child_matrix * nested, style)
            elif tag == "use":
                reference = (child.get("href") or "").lstrip("#")
                target = self.ids.get(reference)
                if target is None:
                    self.warn("a <use> pointing at '%s', which is not in the file, was skipped" % reference)
                    continue
                offset = Matrix(e = length(child.get("x")), f = length(child.get("y")))
                if target.tag == "symbol":
                    #a symbol is only ever drawn through a <use> - as a group, here
                    symbol = ElementTree.Element("g", {k: v for k, v in target.attrib.items() if k != "id"})
                    symbol.extend(list(target))
                    target = symbol
                holder = ElementTree.Element("g")
                holder.append(target)
                self.walk(holder, child_matrix * offset, style)
            elif tag in ("rect", "circle", "ellipse", "line", "polyline", "polygon", "path"):
                if style.get("visibility") not in ("hidden", "collapse"):
                    self.addGeometry(child, tag, child_matrix, style)
            elif tag == "text":
                if style.get("visibility") not in ("hidden", "collapse"):
                    self.addText(child, child_matrix, style)
            elif tag == "image":
                self.warn("images are not picker shapes - %s skipped" % ("one" if "image" not in self.counts else "some"))
                self.counts["image"] = self.counts.get("image", 0) + 1
            else:
                self.walk(child, child_matrix, style)

    # -- shapes

    def styled(self, shape, style, matrix, has_fill = True):
        opacity = style["group-opacity"]
        fill_on, fill_color = self.colorFor(style.get("fill"), style, float(style.get("fill-opacity", 1.0)))
        stroke_on, stroke_color = self.colorFor(style.get("stroke"), style, float(style.get("stroke-opacity", 1.0)))
        shape["fill"] = {"enabled": fill_on and has_fill, "color": fill_color}
        shape["outline"] = {"enabled": stroke_on, "color": stroke_color,
                            "width": round(length(style.get("stroke-width"), 1.0) * matrix.scale(), 3)}
        shape["opacity"] = round(opacity, 3)
        return shape

    def addGeometry(self, element, tag, matrix, style):
        name = self.nameFor(element, tag)
        number = lambda key, default = 0.0: length(element.get(key), default)

        if tag == "rect":
            x, y, w, h = number("x"), number("y"), number("width"), number("height")
            if w <= 0 or h <= 0:
                return
            rx = number("rx", -1.0); ry = number("ry", -1.0)
            rx, ry = (rx if rx >= 0 else max(ry, 0.0)), (ry if ry >= 0 else max(rx, 0.0))
            rx, ry = min(rx, w / 2.0), min(ry, h / 2.0)
            if matrix.isAxisAligned() and abs(rx - ry) < 1e-6:
                (x1, y1), (x2, y2) = matrix.apply(x, y), matrix.apply(x + w, y + h)
                shape = document_model.newShape("rect", min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1), name)
                shape["radius"] = rx * abs(matrix.a)
            else:
                shape = document_model.newPolygon(roundedRectPoints(x, y, w, h, rx, ry, matrix), name)
            self.shapes.append(self.styled(shape, style, matrix))
            return

        if tag in ("circle", "ellipse"):
            cx, cy = number("cx"), number("cy")
            rx = number("r") if tag == "circle" else number("rx")
            ry = number("r") if tag == "circle" else number("ry")
            if rx <= 0 or ry <= 0:
                return
            if matrix.isAxisAligned():
                (x1, y1), (x2, y2) = matrix.apply(cx - rx, cy - ry), matrix.apply(cx + rx, cy + ry)
                shape = document_model.newShape("ellipse", min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1), name)
            else:
                shape = document_model.newPolygon(ellipsePoints(cx, cy, rx, ry, matrix), name)
            self.shapes.append(self.styled(shape, style, matrix))
            return

        if tag == "line":
            subpaths = [([matrix.apply(number("x1"), number("y1")), matrix.apply(number("x2"), number("y2"))], False)]
        elif tag in ("polyline", "polygon"):
            values = [float(v) for v in NUMBER.findall(element.get("points") or "")]
            points = cleanPoints([matrix.apply(values[i], values[i + 1]) for i in range(0, len(values) - 1, 2)])
            subpaths = [(points, tag == "polygon")] if len(points) > 1 else []
        else:
            subpaths = parsePath(element.get("d"), matrix)
        if not subpaths:
            return

        fill_on, _ = self.colorFor(style.get("fill"), style, 1.0)
        stroke_on, _ = self.colorFor(style.get("stroke"), style, 1.0)
        fill_rule = "evenodd" if style.get("fill-rule") == "evenodd" else "nonzero"
        open_subpaths = [points for points, closed in subpaths if not closed]

        #the fill: every subpath an outline, open ones closed the way SVG fills them
        fillable = [points for points, _ in subpaths if len(points) > 2]
        if fill_on and tag != "line" and fillable:
            shape = self.polygonFrom(fillable, fill_rule, name)
            self.styled(shape, style, matrix)
            #a closed outline can keep its stroke; open ones get theirs below
            if open_subpaths:
                shape["outline"]["enabled"] = False
            self.shapes.append(shape)
        elif stroke_on and not open_subpaths:
            #outline only, all closed - an unfilled shape with an outline
            shape = self.polygonFrom([p for p, _ in subpaths], fill_rule, name)
            self.shapes.append(self.styled(shape, style, matrix, has_fill = False))

        #open subpaths with a stroke: the stroke itself, as a filled shape
        if stroke_on and open_subpaths:
            width = length(style.get("stroke-width"), 1.0) * matrix.scale()
            outline = self.strokeOutline(open_subpaths, width, style)
            if outline:
                shape = self.polygonFrom(outline, "nonzero", name + ("_stroke" if fill_on else ""))
                self.styled(shape, style, matrix)
                _, stroke_color = self.colorFor(style.get("stroke"), style, float(style.get("stroke-opacity", 1.0)))
                shape["fill"] = {"enabled": True, "color": stroke_color}
                shape["outline"]["enabled"] = False
                self.shapes.append(shape)

    def polygonFrom(self, contours, fill_rule, name):
        if len(contours) == 1:
            return document_model.newPolygon(contours[0], name)
        return document_model.newContourPolygon(contours, fill_rule, name)

    def strokeOutline(self, open_subpaths, width, style):
        """The area an open line's stroke covers, as outlines."""
        path = QtGui.QPainterPath()
        for points in open_subpaths:
            path.moveTo(*points[0])
            for point in points[1:]:
                path.lineTo(*point)
        stroker = QtGui.QPainterPathStroker()
        stroker.setWidth(max(width, 0.1))
        stroker.setCapStyle({"round": QtCore.Qt.RoundCap, "square": QtCore.Qt.SquareCap}.get(
            style.get("stroke-linecap"), QtCore.Qt.FlatCap))
        stroker.setJoinStyle({"round": QtCore.Qt.RoundJoin, "bevel": QtCore.Qt.BevelJoin}.get(
            style.get("stroke-linejoin"), QtCore.Qt.MiterJoin))
        stroke = stroker.createStroke(path).simplified()
        return [[(p.x(), p.y()) for p in polygon][:-1] for polygon in stroke.toSubpathPolygons()
                if polygon.size() > 3]

    def addText(self, element, matrix, style):
        content = " ".join(" ".join(element.itertext()).split())
        if not content:
            return
        x = length(element.get("x"))
        y = length(element.get("y"))
        size = length(style.get("font-size"), 16.0) * matrix.scale()
        anchor = style.get("text-anchor", "start")
        bold = style.get("font-weight") in ("bold", "bolder", "600", "700", "800", "900")
        font = QtGui.QFont("Verdana")
        font.setPixelSize(max(int(round(size)), 1))
        font.setBold(bold)
        metrics = QtGui.QFontMetricsF(font)
        width = metrics.horizontalAdvance(content) + 4
        height = metrics.height()
        baseline_x, baseline_y = matrix.apply(x, y)
        left = {"middle": baseline_x - width / 2.0, "end": baseline_x - width}.get(anchor, baseline_x)
        shape = document_model.newShape("text", left, baseline_y - metrics.ascent(), width, height,
                                        self.nameFor(element, "text"))
        fill_on, fill_color = self.colorFor(style.get("fill"), style, float(style.get("fill-opacity", 1.0)))
        shape["text"].update(content = content, size = round(size, 2), color = fill_color, bold = bold,
                             align = {"middle": "center", "end": "right"}.get(anchor, "left"))
        shape["opacity"] = round(style["group-opacity"], 3)
        if not matrix.isAxisAligned():
            self.warn("turned text is placed upright")
        self.shapes.append(shape)


def shapeBounds(shapes):
    left = min(s["x"] for s in shapes); top = min(s["y"] for s in shapes)
    right = max(s["x"] + s["w"] for s in shapes); bottom = max(s["y"] + s["h"] for s in shapes)
    return left, top, right, bottom


def placeShapes(shapes, scale, dx, dy):
    """Scale every shape about the origin, then move it - uniformly, so a
    rectangle stays a rectangle."""
    for shape in shapes:
        document_model.resizeShape(shape, shape["x"] * scale + dx, shape["y"] * scale + dy,
                                   shape["w"] * scale, shape["h"] * scale)
        shape["radius"] = shape.get("radius", 0) * scale
        shape["outline"]["width"] = round(shape["outline"]["width"] * scale, 3)
        shape["text"]["size"] = round(shape["text"]["size"] * scale, 2)


def importSvg(path, page_width, page_height):
    """(shapes, warnings, scale) - the SVG at `path` as picker shapes on a page
    of this size. A drawing larger than the page is fitted onto it; one that
    fits keeps its size, moved onto the page if it starts off it."""
    try:
        root = ElementTree.parse(path).getroot()
    except ElementTree.ParseError as error:
        raise ValueError("not a readable SVG file: %s" % error)
    importer = SvgImporter(page_width, page_height)
    importer.read(root)
    shapes = importer.shapes
    if not shapes:
        return [], importer.warnings + ["nothing in the file could be turned into shapes"], 1.0

    left, top, right, bottom = shapeBounds(shapes)
    width, height = max(right - left, 1e-6), max(bottom - top, 1e-6)
    if width > page_width or height > page_height:
        #too big for the page: scaled down to fit, with a margin
        scale = min((page_width - 2 * FIT_MARGIN) / width, (page_height - 2 * FIT_MARGIN) / height)
        placeShapes(shapes, scale, FIT_MARGIN - left * scale, FIT_MARGIN - top * scale)
        return shapes, importer.warnings, scale
    #fits: kept at its own size, only moved onto the page if it starts off it
    dx = -left if left < 0 else min(0.0, page_width - right)
    dy = -top if top < 0 else min(0.0, page_height - bottom)
    if dx or dy:
        placeShapes(shapes, 1.0, dx, dy)
    return shapes, importer.warnings, 1.0
