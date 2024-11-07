from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable
from MNRB_UI.node_Editor_UI.node_Editor_GraphicScene import NodeEditor_GraphicScene

CLASS_DEBUG = True

class NodeEditorScene(Serializable):
    def __init__(self):

        self.grScene = NodeEditor_GraphicScene(self)

        if CLASS_DEBUG : print("NODE_EDITOR_SCENE:: -__init__:: Initialized Node Editor SCENE")

