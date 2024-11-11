
class NodeEditor_QGraphicEdgePathBase():
    def __init__(self, parent):
        self.parent=parent

    def calculatePath(self):
        return None

class NodeEditor_QGaphicEdgePathDirect(NodeEditor_QGraphicEdgePathBase):
    def calculatePath(self):
        return None

class NodeEditor_QGraphicEdgePathBezier(NodeEditor_QGraphicEdgePathBase):
   def calculatePath(self):
        return None