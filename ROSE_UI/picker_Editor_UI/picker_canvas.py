"""The picker editor's canvas: the page, its shapes, and the drawing tools.

Shapes are painted with picker_runtime.paintShape - the same code the exported
picker uses, so what is drawn here is what the animator gets.

Each item wraps one shape dict of the document and edits it in place; the tab
is told when an edit is finished (commitEdit) so it can record an undo step.
"""

from PySide6 import QtCore, QtGui, QtWidgets #type: ignore

from MNRB.ROSE_UI.picker_Editor_UI import picker_runtime as runtime #type: ignore
from MNRB.ROSE_UI.picker_Editor_UI import picker_document as document_model #type: ignore

HANDLE_SIZE = 8.0
SELECTION_COLOR = QtGui.QColor("#FFA637")
GRID = 5.0
#a click without a drag creates a shape of this size
DEFAULT_SIZE = {"rect": (80, 40), "ellipse": (50, 50), "text": (100, 30)}

TOOL_SELECT = "select"
TOOL_RECT = "rect"
TOOL_ELLIPSE = "ellipse"
TOOL_POLYGON = "polygon"
TOOL_TEXT = "text"

#corner handles: which edges each one moves (left, top, right, bottom)
CORNERS = {"topLeft": (True, True, False, False), "topRight": (False, True, True, False),
           "bottomLeft": (True, False, False, True), "bottomRight": (False, False, True, True)}


class ShapeItem(QtWidgets.QGraphicsItem):
    """One shape on the canvas. Moved by dragging it, resized by its corner
    handles, a polygon reshaped by its vertex handles."""

    def __init__(self, shape, canvas):
        super().__init__()
        self.shape_data = shape
        self.canvas = canvas
        self.drag = None
        #set while the item is placed from the data - that is not a drag, and must
        #not be snapped
        self.syncing = False
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.syncFromShape()

    def syncFromShape(self):
        self.prepareGeometryChange()
        self.syncing = True
        self.setPos(self.shape_data["x"], self.shape_data["y"])
        self.syncing = False
        self.update()

    def handleScale(self):
        view = self.canvas.views()[0] if self.canvas.views() else None
        zoom = view.transform().m11() if view else 1.0
        return HANDLE_SIZE / max(zoom, 1e-3)

    def boundingRect(self):
        margin = self.shape_data.get("outline", {}).get("width", 0) + self.handleScale()
        return QtCore.QRectF(-margin, -margin, self.shape_data["w"] + 2 * margin, self.shape_data["h"] + 2 * margin)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(QtCore.QRectF(0, 0, self.shape_data["w"], self.shape_data["h"]))
        return path

    def paint(self, painter, option, widget = None):
        runtime.paintShape(painter, self.shape_data)
        if self.isSelected():
            pen = QtGui.QPen(SELECTION_COLOR)
            pen.setCosmetic(True)
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRect(QtCore.QRectF(0, 0, self.shape_data["w"], self.shape_data["h"]))
            if len(self.canvas.selectedItems()) == 1:
                painter.setBrush(QtGui.QBrush(SELECTION_COLOR))
                pen.setStyle(QtCore.Qt.SolidLine)
                painter.setPen(pen)
                for rect in self.handleRects().values():
                    painter.drawRect(rect)
                painter.setBrush(QtGui.QBrush(QtGui.QColor("#FFFFFF")))
                for _, rect in self.vertexRects():
                    painter.drawEllipse(rect)

    def handleRects(self):
        size = self.handleScale()
        w, h = self.shape_data["w"], self.shape_data["h"]
        centers = {"topLeft": (0, 0), "topRight": (w, 0), "bottomLeft": (0, h), "bottomRight": (w, h)}
        return {name: QtCore.QRectF(x - size / 2, y - size / 2, size, size) for name, (x, y) in centers.items()}

    def vertexRects(self):
        """[((outline, point), rect)] for a polygon's points."""
        if self.shape_data["type"] != "polygon":
            return []
        size = self.handleScale()
        return [((contour_index, point_index), QtCore.QRectF(x - size / 2, y - size / 2, size, size))
                for contour_index, contour in enumerate(runtime.getContours(self.shape_data))
                for point_index, (x, y) in enumerate(contour)]

    def handleAt(self, point):
        if not self.isSelected() or len(self.canvas.selectedItems()) != 1:
            return None
        for index, rect in self.vertexRects():
            if rect.contains(point):
                return ("vertex", index)
        for name, rect in self.handleRects().items():
            if rect.contains(point):
                return ("corner", name)
        return None

    def mousePressEvent(self, event):
        handle = self.handleAt(event.pos())
        if handle and event.button() == QtCore.Qt.LeftButton:
            self.drag = handle
            self.drag_start = dict(x = self.shape_data["x"], y = self.shape_data["y"],
                                   w = self.shape_data["w"], h = self.shape_data["h"])
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag is None:
            return super().mouseMoveEvent(event)
        point = self.canvas.snapPoint(event.scenePos())
        kind, which = self.drag
        if kind == "corner":
            left_moves, top_moves, right_moves, bottom_moves = CORNERS[which]
            start = self.drag_start
            left, top = start["x"], start["y"]
            right, bottom = left + start["w"], top + start["h"]
            if left_moves: left = min(point.x(), right - 1)
            if right_moves: right = max(point.x(), left + 1)
            if top_moves: top = min(point.y(), bottom - 1)
            if bottom_moves: bottom = max(point.y(), top + 1)
            self.prepareGeometryChange()
            document_model.resizeShape(self.shape_data, left, top, right - left, bottom - top)
        else:
            self.moveVertex(which, point)
        self.syncFromShape()
        self.canvas.shapeEdited(self, live = True)

    def moveVertex(self, index, page_point):
        """Move one polygon point; the box is refitted around the points."""
        shape = self.shape_data
        contour_index, point_index = index
        contours = [[[shape["x"] + px, shape["y"] + py] for px, py in contour]
                    for contour in runtime.getContours(shape)]
        contours[contour_index][point_index] = [page_point.x(), page_point.y()]
        self.prepareGeometryChange()
        if shape.get("contours"):
            refit = document_model.newContourPolygon(contours, shape.get("fill_rule", "nonzero"))
            shape.update(x = refit["x"], y = refit["y"], w = refit["w"], h = refit["h"], contours = refit["contours"])
        else:
            refit = document_model.newPolygon(contours[0])
            shape.update(x = refit["x"], y = refit["y"], w = refit["w"], h = refit["h"], points = refit["points"])

    def mouseReleaseEvent(self, event):
        if self.drag is not None:
            self.drag = None
            self.canvas.shapeEdited(self, live = False)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange and self.scene() is not None and not self.syncing:
            return self.canvas.snapPoint(value)
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            self.shape_data["x"], self.shape_data["y"] = self.pos().x(), self.pos().y()
        return super().itemChange(change, value)

    def hoverMoveEvent(self, event):
        handle = self.handleAt(event.pos())
        if handle and handle[0] == "corner":
            self.setCursor(QtCore.Qt.SizeFDiagCursor if handle[1] in ("topLeft", "bottomRight")
                           else QtCore.Qt.SizeBDiagCursor)
        elif handle:
            self.setCursor(QtCore.Qt.CrossCursor)
        else:
            self.setCursor(QtCore.Qt.SizeAllCursor)
        super().hoverMoveEvent(event)


class PickerCanvas(QtWidgets.QGraphicsScene):
    """The page and its shapes. Owns nothing of its own - the document is the
    tab's; this only shows and edits it."""

    def __init__(self, tab):
        super().__init__()
        self.tab = tab
        self.snap = True
        self.items_by_id = {}

    @property
    def page(self):
        return self.tab.document["page"]

    def snapPoint(self, point):
        if not self.snap:
            return QtCore.QPointF(point)
        return QtCore.QPointF(round(point.x() / GRID) * GRID, round(point.y() / GRID) * GRID)

    def rebuild(self, selected_ids = ()):
        self.blockSignals(True)
        self.clear()
        self.items_by_id = {}
        page = self.page
        self.setSceneRect(QtCore.QRectF(-200, -200, page["width"] + 400, page["height"] + 400))
        for index, shape in enumerate(self.tab.document["shapes"]):
            item = ShapeItem(shape, self)
            item.setZValue(index)
            self.addItem(item)
            self.items_by_id[shape["id"]] = item
            item.setSelected(shape["id"] in selected_ids)
            item.setToolTip(self.tab.describeAction(shape))
        self.blockSignals(False)
        self.selectionChanged.emit()

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QtGui.QColor("#1C1C1C"))
        page_rect = QtCore.QRectF(0, 0, self.page["width"], self.page["height"])
        painter.fillRect(page_rect, runtime.toColor(self.page.get("background"), "#2B2B2B"))
        if self.snap:
            pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 14))
            pen.setCosmetic(True)
            painter.setPen(pen)
            step = GRID * 4
            x = 0.0
            while x <= page_rect.width():
                painter.drawLine(QtCore.QLineF(x, 0, x, page_rect.height())); x += step
            y = 0.0
            while y <= page_rect.height():
                painter.drawLine(QtCore.QLineF(0, y, page_rect.width(), y)); y += step
        pen = QtGui.QPen(QtGui.QColor("#555555"))
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawRect(page_rect)

    def selectedShapes(self):
        return [item.shape_data for item in self.selectedItems() if isinstance(item, ShapeItem)]

    def shapeEdited(self, item, live):
        self.tab.onShapesEdited(live)


class PickerView(QtWidgets.QGraphicsView):
    """Draws shapes with the current tool, pans with the middle mouse button,
    zooms with the wheel."""

    def __init__(self, canvas, tab):
        super().__init__(canvas)
        self.tab = tab
        self.tool = TOOL_SELECT
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.creating_start = None
        self.preview = None
        self.polygon_points = []
        self.panning = None
        self.moved_items = False

    def setTool(self, tool):
        self.cancelCreation()
        self.tool = tool
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag if tool == TOOL_SELECT
                         else QtWidgets.QGraphicsView.NoDrag)
        self.viewport().setCursor(QtCore.Qt.ArrowCursor if tool == TOOL_SELECT else QtCore.Qt.CrossCursor)
        self.tab.onToolChanged(tool)

    def frame(self):
        page = self.tab.document["page"]
        self.fitInView(QtCore.QRectF(-20, -20, page["width"] + 40, page["height"] + 40), QtCore.Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def scenePoint(self, event):
        return self.tab.canvas.snapPoint(self.mapToScene(event.position().toPoint()))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.panning = event.position()
            self.viewport().setCursor(QtCore.Qt.ClosedHandCursor)
            return
        if event.button() == QtCore.Qt.LeftButton and self.tool != TOOL_SELECT:
            point = self.scenePoint(event)
            if self.tool == TOOL_POLYGON:
                self.polygon_points.append((point.x(), point.y()))
                self.updatePreview(point)
            else:
                self.creating_start = point
                self.updatePreview(point)
            return
        self.moved_items = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning is not None:
            delta = event.position() - self.panning
            self.panning = event.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
            return
        if self.tool != TOOL_SELECT and (self.creating_start is not None or self.polygon_points):
            self.updatePreview(self.scenePoint(event))
            return
        if event.buttons() & QtCore.Qt.LeftButton and self.tab.canvas.selectedItems():
            self.moved_items = True
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton and self.panning is not None:
            self.panning = None
            self.setTool(self.tool)
            return
        if event.button() == QtCore.Qt.LeftButton and self.creating_start is not None:
            start, end = self.creating_start, self.scenePoint(event)
            self.creating_start = None
            self.clearPreview()
            self.createBoxShape(start, end)
            return
        super().mouseReleaseEvent(event)
        if self.moved_items:
            self.moved_items = False
            self.tab.onShapesEdited(live = False)

    def mouseDoubleClickEvent(self, event):
        if self.tool == TOOL_POLYGON:
            self.finishPolygon()
            return
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if self.tool == TOOL_POLYGON and event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.finishPolygon()
            return
        if event.key() == QtCore.Qt.Key_Escape:
            if self.tool != TOOL_SELECT:
                self.setTool(TOOL_SELECT)
            else:
                self.tab.canvas.clearSelection()
            return
        if event.key() in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            self.tab.onDelete()
            return
        super().keyPressEvent(event)

    def createBoxShape(self, start, end):
        width, height = abs(end.x() - start.x()), abs(end.y() - start.y())
        left, top = min(start.x(), end.x()), min(start.y(), end.y())
        if width < 4 and height < 4:
            width, height = DEFAULT_SIZE[self.tool]
        self.tab.addShape(document_model.newShape(self.tool, left, top, max(width, 4), max(height, 4),
                                                  self.tab.nextShapeName(self.tool)))
        self.setTool(TOOL_SELECT)

    def finishPolygon(self):
        #a double-click lands two points on the same spot - one is enough
        points = []
        for point in self.polygon_points:
            if not points or QtCore.QLineF(QtCore.QPointF(*points[-1]), QtCore.QPointF(*point)).length() > 1:
                points.append(point)
        self.clearPreview()
        self.polygon_points = []
        if len(points) >= 3:
            self.tab.addShape(document_model.newPolygon(points, self.tab.nextShapeName("polygon")))
        self.setTool(TOOL_SELECT)

    def cancelCreation(self):
        self.creating_start = None
        self.polygon_points = []
        self.clearPreview()

    def updatePreview(self, point):
        path = QtGui.QPainterPath()
        if self.tool == TOOL_POLYGON:
            if not self.polygon_points:
                return
            path.moveTo(*self.polygon_points[0])
            for p in self.polygon_points[1:]:
                path.lineTo(*p)
            path.lineTo(point)
        else:
            rect = QtCore.QRectF(self.creating_start, point).normalized()
            if self.tool == TOOL_ELLIPSE:
                path.addEllipse(rect)
            else:
                path.addRect(rect)
        if self.preview is None:
            self.preview = self.tab.canvas.addPath(path)
            pen = QtGui.QPen(SELECTION_COLOR)
            pen.setCosmetic(True)
            pen.setStyle(QtCore.Qt.DashLine)
            self.preview.setPen(pen)
            self.preview.setZValue(1e6)
        else:
            self.preview.setPath(path)

    def clearPreview(self):
        if self.preview is not None:
            self.tab.canvas.removeItem(self.preview)
            self.preview = None
