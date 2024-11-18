

class NodeEditorSceneClipboard():
    def __init__(self, scene) -> None:
        self.scene = scene


    def serializeSceneToClipboard(self, delete=False):
        return {}

    def deserializeFromClipboardToScene(self, data):
        print("Deserializing from Clipboard with data:: ", data)