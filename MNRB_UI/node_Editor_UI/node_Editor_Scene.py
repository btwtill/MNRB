from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene import NodeEditor_QGraphicScene # type: ignore
from MNRB.MNRB_UI.mnrb_ui_utils import findIndexByAttribute #type: ignore

CLASS_DEBUG = False

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
        if CLASS_DEBUG: 
            print("NODE_EDITOR_SCENE:: -removeNode:: Before:: Nodes:: ")
            print("NODE_EDITOR_SCENE:: -removeNode:: \t\t Amount", len(self.nodes))
            for index, _node in enumerate(self.nodes):
                print("NODE_EDITOR_SCENE:: -removeNode:: \t\t", _node, " at Index:: ", index, " with ID: ", _node.id)
            print("NODE_EDITOR_SCENE:: -removeNode:: Index of node to be Removed:: ", findIndexByAttribute(self.nodes, node.id))
        
        index_node_remove = findIndexByAttribute(self.nodes, node.id)
        #self.nodes.remove(node)
        del self.nodes[index_node_remove]

        if CLASS_DEBUG: 
            print("NODE_EDITOR_SCENE:: -removeNode:: After:: After:: ")
            print("NODE_EDITOR_SCENE:: -removeNode:: \t\t Amount", len(self.nodes))
            for index, _node in enumerate(self.nodes):
                print("NODE_EDITOR_SCENE:: -removeNode:: \t\t", _node, " at Index:: ", index, " with ID: ", _node.id)
    
    def removeEdge(self, edge):
        if CLASS_DEBUG: 
            print("NODE_EDITOR_SCENE:: -removeEdge:: Before:: Edges:: ")
            print("NODE_EDITOR_SCENE:: -removeEdge:: \t\t Amount", len(self.edges))
            for index, _edge in enumerate(self.edges):
                print("NODE_EDITOR_SCENE:: -removeEdge:: \t\t", _edge, " at Index:: ", index, " with ID: ", _edge.id)
            print("NODE_EDITOR_SCENE:: -removeNode:: Index of edge to be Removed:: ", findIndexByAttribute(self.edges, edge.id))

        index_edge_remove = findIndexByAttribute(self.edges, edge.id)
        #self.edges.remove(edge)
        del self.edges[index_edge_remove]

        if CLASS_DEBUG:
            print("NODE_EDITOR_SCENE:: -removeEdge:: After:: Edges:: ")
            print("NODE_EDITOR_SCENE:: -removeEdge:: \t\t Amount", len(self.edges))
            for index, _edge in enumerate(self.edges):
                print("NODE_EDITOR_SCENE:: -removeEdge:: \t\t", _edge , " at Index:: ", index, " with ID: ", _edge.id)

