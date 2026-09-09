from PySide6 import QtWidgets #type: ignore
from PySide6.QtCore import Qt, QRectF #type: ignore
from PySide6.QtGui import QColor, QPen, QBrush, QPainterPath, QFont, QFontMetrics #type: ignore
from MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode import NodeEditor_QGraphicNode #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_categories import (CATEGORY_SOURCE, CATEGORY_TARGET, #type: ignore
                                                                          CATEGORY_OPERATOR)

#Deliberately unlike a ROSE component node, which is a squared-off dark card with
#an amber selection and a validity bar. These are pill-shaped, lighter, and carry
#a thick category stripe down their left edge - so at a glance you can tell an
#attribute graph from a rig graph even at low zoom, and tell the three node roles
#apart within it.
#a node whose source is gone: same red the Skinning tab uses for a deform that
#no longer resolves, so "this is what Remove Deprecated will clear" reads the
#same way in both tabs
DEPRECATED_COLOR = QColor("#FFc43721")
DEPRECATED_TINT = QColor(140, 45, 35, 90)

CATEGORY_COLORS = {
    CATEGORY_SOURCE:   QColor("#FF4FA3C7"),   #blue   - something a value comes from
    CATEGORY_TARGET:   QColor("#FF6FBF73"),   #green  - something a value lands on
    CATEGORY_OPERATOR: QColor("#FFB07CC7"),   #purple - something that transforms it
}

class AttributeEditor_QGraphicNode(NodeEditor_QGraphicNode):

    def initGraphicElements(self):
        super().initGraphicElements()

        self.width = 200
        self.title_height = 22
        #where the owning component's name goes - without it, two components'
        #Control_Visibility attributes are indistinguishable on the canvas
        self._subtitle_height = 15

        #pill ends rather than the ROSE node's tight 5px corners
        self._edge_roundness = 11
        self._edge_padding = 6

        self._category_stripe_width = 5.0

        self._title_font = QFont("Verdana", 8, QFont.Bold)
        self._subtitle_font = QFont("Verdana", 7)
        self._socket_label_font = QFont("Verdana", 6)

        #a lighter body than the rig canvas, so the two never get confused
        self._title_backgroundColor = QColor("#FF2E2E33")
        self._content_color = QColor("#EF3A3A41")
        self._selected_color = QColor("#FFFFFFFF")
        self._subtitle_color = QColor("#FF9A9AA5")
        self._socket_label_color = QColor("#FF8A8A95")

        self._title_background_brush = QBrush(self._title_backgroundColor)
        self._content_brush = QBrush(self._content_color)
        self._selected_pen = QPen(self._selected_color)
        self._selected_pen.setWidthF(2.0)

        self._invalid_color = QColor("#FFc43721")
        self._invalid_brush = QBrush(self._invalid_color)

    def getCategoryColor(self):
        #a deprecated node loses its category colour entirely - what it used to be
        #matters less than the fact that it is about to be removed
        if self.node.isDeprecated():
            return DEPRECATED_COLOR

        category = getattr(self.node, "category", CATEGORY_OPERATOR)
        return CATEGORY_COLORS.get(category, CATEGORY_COLORS[CATEGORY_OPERATOR])

    def getSocketRowHeight(self):
        return self.socket_padding + self.socket_radius * 2

    def wrapGrNodeToSockets(self):
        """Size from the sockets themselves.

        The inherited version measures the per-socket *labels* in the content
        widget, and these nodes have no content widget - so it would leave every
        node at the 60px floor no matter how many sockets it grew.
        """
        all_sockets = self.node.inputs + self.node.outputs
        sockets_exist = bool(all_sockets) and hasattr(all_sockets[0], 'hasEdge')

        if self.display_mode == self.DISPLAY_MODE_COLLAPSED:
            self._height = self.title_height + self.socket_padding
            self.width = self.collapsed_width
        else:
            #inputs and outputs stack independently, so the taller side decides
            rows = max(len(self.node.inputs), len(self.node.outputs), 1)
            self._height = max(self.title_height + self._subtitle_height
                               + rows * self.getSocketRowHeight() + self.socket_padding, 60)

        self.title_item.setTextWidth(self.width - 2 * self._title_padding)
        self.title = self._raw_title

        if sockets_exist:
            for socket in all_sockets:
                socket.setPosition()

    def paint(self, painter, option, widget = None):
        body_path = QPainterPath()
        body_path.addRoundedRect(0, 0, self.width, self.height,
                                 self._edge_roundness, self._edge_roundness)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._content_brush)
        painter.drawPath(body_path)

        #title band and stripe clipped to the rounded body, so neither squares off a corner
        painter.save()
        painter.setClipPath(body_path)

        painter.setBrush(self._title_background_brush)
        painter.drawRect(QRectF(0, 0, self.width, self.title_height))

        painter.setBrush(QBrush(self.getCategoryColor()))
        painter.drawRect(QRectF(0, 0, self._category_stripe_width, self.height))

        if self.node.isDeprecated():
            #tint the whole body, not just a bar - this one is going away, and it
            #should be obvious at a glance which nodes Remove Deprecated will take
            painter.setBrush(QBrush(DEPRECATED_TINT))
            painter.drawRect(QRectF(0, 0, self.width, self.height))
        elif not self.node.properties.is_valid:
            painter.setBrush(self._invalid_brush)
            painter.drawRect(QRectF(0, self.title_height, self.width, 2.0))

        painter.restore()

        self.paintSubtitle(painter)
        if self.display_mode != self.DISPLAY_MODE_COLLAPSED:
            self.paintSocketLabels(painter)

        painter.setPen(self._default_pen if not self.isSelected() else self._selected_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(body_path)

        if self.is_drawing_bounding_box:
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawRect(self.boundingRect())

    def paintSubtitle(self, painter):
        subtitle = "%s  (missing)" % self.node.getSubtitle() if self.node.isDeprecated() else self.node.getSubtitle()
        if not subtitle or self.display_mode == self.DISPLAY_MODE_COLLAPSED:
            return

        available_width = self.width - self._title_padding - self._category_stripe_width - 4
        elided = QFontMetrics(self._subtitle_font).elidedText(subtitle, Qt.ElideMiddle, int(available_width))

        painter.setFont(self._subtitle_font)
        painter.setPen(QPen(DEPRECATED_COLOR if self.node.isDeprecated() else self._subtitle_color))
        painter.drawText(QRectF(self._title_padding, self.title_height,
                                available_width, self._subtitle_height),
                         Qt.AlignVCenter | Qt.AlignLeft, elided)

    def paintSocketLabels(self, painter):
        """Socket names drawn straight onto the node.

        A two-input operator is unusable without them, and drawing them here
        avoids reintroducing the content widget these nodes deliberately drop.
        """
        painter.setFont(self._socket_label_font)
        painter.setPen(QPen(self._socket_label_color))
        metrics = QFontMetrics(self._socket_label_font)
        label_height = metrics.height()

        for socket in self.node.inputs:
            position = socket.getPosition()
            painter.drawText(QRectF(self._category_stripe_width + 4, position[1] - label_height / 2,
                                    self.width / 2, label_height),
                             Qt.AlignVCenter | Qt.AlignLeft, str(socket.socket_value))

        for socket in self.node.outputs:
            position = socket.getPosition()
            painter.drawText(QRectF(self.width / 2, position[1] - label_height / 2,
                                    self.width / 2 - 8, label_height),
                             Qt.AlignVCenter | Qt.AlignRight, str(socket.socket_value))
