"""Drawing a library shape's preview from its stored curve points.

Previews are the shape's own sampled polylines rather than rendered images: they
need no viewport or playblast, stay sharp at any size, and cannot drift out of
date with the shape, since both are written by the same library call.
"""

import math

from PySide6.QtCore import Qt, QPointF #type: ignore
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QPolygonF #type: ignore

#a three-quarter view, so a shape flat on any one plane still reads as a shape
VIEW_YAW = math.radians(35.0)
VIEW_PITCH = math.radians(30.0)

BACKGROUND_COLOR = QColor("#2B2B2B")
LINE_COLOR = QColor("#E0C050")
MARGIN = 0.12


def projectPoint(point):
    x, y, z = point
    #turn about Y, then tip about X, then drop the depth
    rotated_x = x * math.cos(VIEW_YAW) + z * math.sin(VIEW_YAW)
    rotated_z = -x * math.sin(VIEW_YAW) + z * math.cos(VIEW_YAW)
    screen_y = y * math.cos(VIEW_PITCH) - rotated_z * math.sin(VIEW_PITCH)
    return rotated_x, screen_y


def buildShapePreviewPixmap(polylines, size = 96, line_color = LINE_COLOR):
    pixmap = QPixmap(size, size)
    pixmap.fill(BACKGROUND_COLOR)

    projected = [[projectPoint(point) for point in polyline] for polyline in polylines]
    all_points = [point for polyline in projected for point in polyline]
    if not all_points:
        return pixmap

    #fitted per shape, so every preview fills its tile whatever the shape's proportions
    min_x = min(point[0] for point in all_points)
    max_x = max(point[0] for point in all_points)
    min_y = min(point[1] for point in all_points)
    max_y = max(point[1] for point in all_points)
    span = max(max_x - min_x, max_y - min_y, 1e-6)
    usable = size * (1.0 - 2.0 * MARGIN)
    scale = usable / span
    offset_x = (size - (max_x - min_x) * scale) / 2.0
    offset_y = (size - (max_y - min_y) * scale) / 2.0

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QPen(line_color, max(1.0, size / 64.0)))
    for polyline in projected:
        polygon = QPolygonF([QPointF(offset_x + (x - min_x) * scale,
                                     #screen Y runs downward
                                     size - offset_y - (y - min_y) * scale)
                             for x, y in polyline])
        painter.drawPolyline(polygon)
    painter.end()

    return pixmap
