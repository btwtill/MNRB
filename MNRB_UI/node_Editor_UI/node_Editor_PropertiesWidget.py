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
        
        
        self.initUI()

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value

    def initUI(self):
        
        self.layout = QVBoxLayout()
        self.id_label = QLabel("ID: " + str(self.id))
        self.layout.addWidget(self.id_label)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def serialize(self):

        serialized_data = OrderedDict([
            ('id', self.id)
        ])

        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id=True):

        if restore_id: self.id =  data['id']

        return True
    

