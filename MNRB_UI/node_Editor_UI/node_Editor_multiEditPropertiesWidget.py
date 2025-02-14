from MNRB.MNRB_UI.node_Editor_UI.node_Editor_PropertiesWidget import NodeEditorPropertiesWidget #type: ignore

CLASS_DEBUG = True

class MultiEdit_PropertyWidget(NodeEditorPropertiesWidget):
    def __init__(self, nodes = [], parent = None):
        super().__init__()
        self.nodes = nodes

        self.title = "Multi Edit Properties"

        if CLASS_DEBUG: print("%s:: MultiEdit_PropertyWidget:: __init__:: " % self.__class__.__name__)
        if CLASS_DEBUG: 
            for node in self.nodes:
                print("%s:: Nodes contained in the multie Edit:: " % self.__class__.__name__, node)

    