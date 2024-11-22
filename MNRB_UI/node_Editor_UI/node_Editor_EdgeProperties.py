from MNRB.MNRB_UI.node_Editor_UI.node_Editor_PropertiesWidget import NodeEditorPropertiesWidget #type: ignore

class NodeEditorEdgeProperties(NodeEditorPropertiesWidget):
    def __init__(self, edge, parent = None):
        super().__init__(parent)
        
        self.edge = edge
        self.title = "Edge Properties"