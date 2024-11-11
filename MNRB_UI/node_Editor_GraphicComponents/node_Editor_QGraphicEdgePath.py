
class NodeEditor_QGraphicEdgePathBase():
    def __init__(self, parent):
        self.parent=parent

    def caclPath(self):
        return None

class NodeEditor_QGaphicEdgePathDirect(NodeEditor_QGraphicEdgePathBase):
    def calcPath(self):
        return None

class NodeEditor_QGraphicEdgePathBezier(NodeEditor_QGraphicEdgePathBase):
   def calcPath(self):
        return None