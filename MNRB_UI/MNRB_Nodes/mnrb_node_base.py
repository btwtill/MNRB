from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore


class MNRB_Node(NodeEditorNode):
    operation_code = 0
    operation_title = "Undefined"

    def __init__(self, scene, inputs=[], outputs=[]):
        super().__init__(scene, self.__class__.operation_title, inputs, outputs)
    