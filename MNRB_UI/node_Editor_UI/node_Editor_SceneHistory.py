
UNDO_DEBUG = True
REDU_DEBUG = True
RESTORE_DEBUG = True
STORE_DEBUG = True

class NodeEditorSceneHistory():
    def __init__(self, scene) -> None:
        self.scene = scene

        self.undo_selection_has_changed = False

        self.history_stack = []
        self.history_current_step = -1
        self.history_limit = 8

    def undo(self):
        if UNDO_DEBUG: print("NODESCENEHISTORY:: --undo:: ")
        if self.history_current_step > 0:
            self.history_current_step -= 1
            self.restoreHistory()
        
    def redo(self):
        if REDU_DEBUG: print("NODESCENEHISTORY:: --redo:: ")
        if self.history_current_step + 1 < len(self.history_stack):
            self.history_current_step += 1
            self.restoreHistory()

    def restoreHistory(self):
        if RESTORE_DEBUG: print("NODESCENEHISTORY:: --restoreHistory:: Restoring ..... Current History Step:: ", self.history_current_step, " History Stack Length:: ", len(self.history_stack))
        self.restoreHistoryStamp(self.history_stack[self.history_current_step])

    def storeHistory(self, history_stamp_description):
        if STORE_DEBUG: print("NODESCENEHISTORY:: --storeHistory:: Storing ..... ", history_stamp_description, "Current History Step:: ", self.history_current_step, " History Stack Length:: ", len(self.history_stack))

        if self.history_current_step +1 < len(self.history_stack):
            self.history_stack = self.history_stack[0:self.history_current_step + 1]

        if self.history_current_step +1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -=1

        history_stamp = self.createHistoryStamp(history_stamp_description)
        self.history_stack.append(history_stamp)
        self.history_current_step += 1

        if STORE_DEBUG: print("NODESCENEHISTORY:: --storeHistory:: setting step:: ", self.history_current_step)

    def restoreHistoryStamp(self, history_stamp):
        if RESTORE_DEBUG: print("NODESCENEHISTORY:: --restoreHistoryStamp:: ", history_stamp)

        self.undo_selection_has_changed = False
        previouse_selection = self.captureCurrentSceneSelection()

        if RESTORE_DEBUG: print("NODESCENEHISTORY:: --restoreHistoryStamp:: Deserializing History Snapshot")
        self.scene.deserialize(history_stamp['snapshot'])
        
        if RESTORE_DEBUG: print("NODESCENEHISTORY:: --restoreHistoryStamp:: Restoring Selection from History Stamp")
        for edge in self.scene.edges: edge.grEdge.setSelected(False)

        for edge_id in history_stamp['selection']['edges']:
            for edge in self.scene.edges:
                if edge.id == edge_id:
                    edge.grEdge.setSelected(True)
                    break

        for node in self.scene.nodes: node.grNode.setSelected(False)

        for node_id in history_stamp['selection']['nodes']:
            for node in self.scene.nodes:
                if node.id == node_id:
                    node.grNode.setSelected(True)
                    break

        current_selection = self.captureCurrentSceneSelection()

    
    def createHistoryStamp(self, history_stamp_description):
        
        history_stamp = {
            'desc': history_stamp_description,
            'snapshot' : self.scene.serialize(),
            'selection': self.captureCurrentSceneSelection()
        }

        return history_stamp

    def captureCurrentSceneSelection(self):
        selectedObjects = {
            'nodes': [],
            'edges': [],
        }
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'): selectedObjects['nodes'].append(item.node.id)
            elif hasattr(item, 'edge'): selectedObjects['edges'].append(item.edge.id)
        return selectedObjects

        