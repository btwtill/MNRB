from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene import NodeEditor_QGraphicScene # type: ignore

CLASS_DEBUG = True

class NodeEditorScene(Serializable):
    def __init__(self):
        super().__init__()
        
        self.grScene = NodeEditor_QGraphicScene(self)
        
        self.nodes = []
        self.edges = []
        
        self.initUI()

        if CLASS_DEBUG : print("NODE_EDITOR_SCENE:: -__init__:: Initialized Node Editor SCENE")

    def initUI(self):
    
        self.grSceneWidth = 64000
        self.grSceneHeight = 64000

        self.grScene.setGrSceneSize(self.grSceneWidth, self.grSceneHeight)

    def addNode(self, node):
        self.nodes.append(node)
    
    def addEdge(self, edge):
        self.edges.append(edge)
    
    def removeNode(self, node):
        if CLASS_DEBUG: print("NODE_EDITOR_SCENE:: -removeNode:: Before:: Nodes:: ", self.nodes)
        self.nodes.remove(node)
        if CLASS_DEBUG: print("NODE_EDITOR_SCENE:: -removeNode:: After:: After:: ", self.nodes)
    
    def removeEdge(self, edge):
        if CLASS_DEBUG: print("NODE_EDITOR_SCENE:: -removeEdge:: Before:: Edges:: ", self.edges)
        self.edges.remove(edge)
        if CLASS_DEBUG: print("NODE_EDITOR_SCENE:: -removeEdge:: After:: Edges:: ", self.edges)

