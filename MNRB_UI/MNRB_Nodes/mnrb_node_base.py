from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore


class MNRB_Node(NodeEditorNode):
    def __init__(self, scene, operation_code, operation_title, inputs=[], outputs=[]):
        self.operation_code = operation_code
        self.operation_title = operation_title

        super().__init__(scene, self.operation_title, inputs, outputs)
    
    