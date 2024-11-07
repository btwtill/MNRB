from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_QGraphicScene import NodeEditor_QGraphicScene # type: ignore

CLASS_DEBUG = True

class NodeEditorScene(Serializable):
    def __init__(self):

        self.grScene = NodeEditor_QGraphicScene(self)
        
        self.initUI()

        if CLASS_DEBUG : print("NODE_EDITOR_SCENE:: -__init__:: Initialized Node Editor SCENE")

    def initUI(self):
    
        self.grSceneWidth = 64000
        self.grSceneHeight = 64000

        self.grScene.setSceneSize(self.grSceneWidth, self.grSceneHeight)


