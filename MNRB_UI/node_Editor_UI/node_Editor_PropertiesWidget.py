from collections import OrderedDict
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel #type: ignore
from PySide2.QtCore import QSize  #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore

EVENT_DEBUG = False

class NodeEditorPropertiesWidget(Serializable, QWidget):
    def __init__(self, parent=None) -> None:
        Serializable.__init__(self)
        QWidget.__init__(self)
        
        self._title = "undefined"
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._is_valid = False
        self._has_been_modified = False

        self._has_been_modified_listeners = []
        self._is_valid_listeners = []

        self.stretch_content = True

        self.initUI()

        if self.stretch_content:
            self.layout.addStretch()
            
        self.initActions()

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
    
    @property
    def has_been_modified(self): return self._has_been_modified
    @has_been_modified.setter
    def has_been_modified(self, value):
        self._has_been_modified = value
        for callback in self._has_been_modified_listeners: callback()

    @property
    def is_valid(self): return self._is_valid
    @is_valid.setter
    def is_valid(self, value):
        self._is_valid = value
        for callback in self._is_valid_listeners: callback(self._is_valid)

    def initUI(self):
        self.id_label = QLabel("ID: " + str(self.id))
        self.layout.addWidget(self.id_label)
    
    def initActions(self):
        pass

    def connectHasBeenModifiedCallback(self, callback):
        self._has_been_modified_listeners.append(callback)

    def connectIsValidCallback(self, callback):
        self._is_valid_listeners.append(callback)

    def setHasBeenModified(self):
        self.has_been_modified = True

    def serialize(self):

        serialized_data = OrderedDict([
            ('id', self.id)
        ])

        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id=True):

        if restore_id: self.id =  data['id']

        return True
    

