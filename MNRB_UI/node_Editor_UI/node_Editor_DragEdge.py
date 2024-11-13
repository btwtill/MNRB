from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket import NodeEditor_QGraphicSocket #type: ignore

CLASS_DEBUG = True

class NodeEditorDragEdge():
    def __init__(self, grView):
        self.grView = grView

        self.drag_edge = None
        self.drag_edge_start_socket = None

    def startEdgeDrag(self, item_on_click):

        if CLASS_DEBUG: print("DRAGEDGE:: --startEdgeDrag:: Start Dragging Edge")
        self.drag_edge_start_socket = item_on_click.socket
        if CLASS_DEBUG: print("DRAGEDGE:: --startEdgeDrag:: \tAssigning Socket: ", item_on_click.socket, " to Drag Edge start Socket!")

    def endEdgeDrag(self, item_on_click):
        
        if CLASS_DEBUG: print("DRAGEDGE:: --endEdgeDrag:: End Dragging Edge")
        if CLASS_DEBUG: print("DRAGEDGE:: -endEdgeDrag:: Remove Dragging Edge")

        if isinstance(item_on_click, NodeEditor_QGraphicSocket):
           
            if item_on_click.socket != self.drag_edge_start_socket:
                if CLASS_DEBUG: print("DRAGEDGE:: --endEdgeDrag:: \tAssigning Socket: ", item_on_click.socket, " to Drag Edge end Socket!")

                for socket in (item_on_click.socket, self.drag_edge_start_socket):
                    if socket.accept_multi_edges:
                        if CLASS_DEBUG: print("DRAGEDGE:: --endEdgeDrag:: Socket:", socket," is not Multi Edged! Removing Old Connected Edges")

                if CLASS_DEBUG: print("DRAGEDGE:: --endEdgeDrag:: Create New Edge from the Drag Edge Data")
            return True

        if CLASS_DEBUG: print("DRAGEDGE:: --endEdgeDrag:: Finished ending Dragging!")
        return False