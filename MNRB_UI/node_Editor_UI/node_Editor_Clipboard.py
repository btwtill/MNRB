from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge import NodeEditor_QGraphicEdge #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import NodeEditorEdge #type: ignore

SERIALIZE_DEBUG = True
DESERIALIZE_DEBUG = True

class NodeEditorSceneClipboard():
    def __init__(self, scene) -> None:
        self.scene = scene


    def serializeSceneToClipboard(self, delete=False):
        if SERIALIZE_DEBUG: print("NODE_EDITOR_CLIPBOARD:: ________________________________START SERIALIZING TO CLIPBOAD")

        selected_nodes, selected_edges, selected_sockets = [], [], {}
        last_mouse_scene_position = OrderedDict([
            ("position_x", self.scene.getView().last_mouse_position.x()),
            ("position_y", self.scene.getView().last_mouse_position.y()),
        ])

        final_edges = []

        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                print("NODE_EDITOR_CLIPBOARD:: I am a Node:: ", item)
                selected_nodes.append(item.node.serialize())
                for socket in (item.node.inputs + item.node.outputs):
                    selected_sockets[socket.id] = socket

            elif isinstance(item, NodeEditor_QGraphicEdge):
                selected_edges.append(item.edge)

        for edge in selected_edges:
            if edge.start_socket.id in selected_sockets and edge.end_socket.id in selected_sockets:
                final_edges.append(edge.serialize())
            
        if delete:
            for node in selected_nodes:
                self.scene.getView().deleteSelected()
                self.scene.history.storeHistory("Cut Elements from Scene", set_modified = True)
        
        if SERIALIZE_DEBUG: 
            print("NODE_EDITOR_CLIPBOARD:: ClipboardContent:: ")
            print("NODE_EDITOR_CLIPBOARD:: \t Nodes:: ", len(selected_nodes) ," Data:: ",selected_nodes)
            print("NODE_EDITOR_CLIPBOARD:: \t Edges:: ", len(selected_edges) ," Data:: " ,final_edges)
            print("NODE_EDITOR_CLIPBOARD:: \t Sockets:: ", len(selected_sockets) ," Data:: " ,selected_sockets)
            print("NODE_EDITOR_CLIPBOARD:: ________________________________END SERIALIZING TO CLIPBOAD")

        return OrderedDict ([
            ("nodes", selected_nodes),
            ("edges", final_edges),
            ("mouse_position", last_mouse_scene_position)
        ])

    def deserializeFromClipboardToScene(self, data):
        if DESERIALIZE_DEBUG: 
            print("NODE_EDITOR_CLIPBOARD:: ________________________________START DESERIALIZING FROM CLIPBOARD")
            print("NODE_EDITOR_CLIPBOARD:: Data to be deserialized:: ", data)

        hashmap = {}

        view = self.scene.getView()
        new_mouse_scene_position = view.last_mouse_position
        old_mouse_scene_position = data["mouse_position"]

        self.scene.doDeselectItems()

        for node_data in data["nodes"]:

            #create the node
            new_node = NodeEditorNode(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id = False)

            #position the node
            old_node_vector = [node_data["position_x"], node_data["position_y"]]

            offest_vector = [old_mouse_scene_position["position_x"] - old_node_vector[0], old_mouse_scene_position["position_y"] - old_node_vector[1]]
            new_node_position = [new_mouse_scene_position.x() - offest_vector[0], new_mouse_scene_position.y() - offest_vector[1]]

            if DESERIALIZE_DEBUG: 
                print("NODE_EDITOR_CLIPBOARD:: Node:: ", node_data["title"])
                print("NODE_EDITOR_CLIPBOARD:: Node:: Old Mouse Position:: x: ", old_mouse_scene_position["position_x"] ," y:",old_mouse_scene_position["position_y"] )
                print("NODE_EDITOR_CLIPBOARD:: Node:: Old Position:: x: ", old_node_vector[0], " y:", old_node_vector[1] )
                print("NODE_EDITOR_CLIPBOARD:: Node:: Offset Positions:: x: ", offest_vector[0], " y:", offest_vector[1] )
                print("NODE_EDITOR_CLIPBOARD:: Node:: New Node Positions:: x: ", new_node_position[0], " y:", new_node_position[1] )

            new_node.setPosition(new_node_position[0], new_node_position[1])

        if "edges" in data:
            for edge_data in data["edges"]:
                new_edge = NodeEditorEdge(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False)
        
        self.scene.history.storeHistory("Pasted Elements to Scene", set_modified = True)



