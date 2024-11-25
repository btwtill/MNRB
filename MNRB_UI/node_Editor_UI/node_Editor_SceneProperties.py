from PySide2 import QtWidgets #type: ignore 
from PySide2.QtCore import Qt #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_PropertiesWidget import NodeEditorPropertiesWidget #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

EVENT_DEBUG = False

class NodeEditorSceneProperties(NodeEditorPropertiesWidget):
    def __init__(self, scene, parent=None) -> None:
        super().__init__(parent)

        self.scene = scene

        self.title = "Scene Properties"
        self.rig_name = "Undefined"
        self.rig_main_geometry = None
        
    def initUI(self):
        #Rig Name
        self.rig_name_label = QtWidgets.QLabel("Define the overall name for your Rig!")
        self.rig_name_label.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(self.rig_name_label)

        self.rig_name_line_edit = QtWidgets.QLineEdit()
        self.rig_name_line_edit.setPlaceholderText("No Name Defined:")
        self.rig_name_line_edit.textChanged.connect(lambda: self.updateRigName(self.rig_name_line_edit.text()))
        self.rig_name_line_edit.textChanged.connect(lambda: self.scene.setModified(True))
        self.layout.addWidget(self.rig_name_line_edit)

        #Main Rig Geometry
        self.main_rig_geometry_layout = QtWidgets.QHBoxLayout()
        self.main_rig_geometry_line_edit = QtWidgets.QLineEdit()
        self.main_rig_geometry_line_edit.setPlaceholderText("No Geometry Defined:")
        self.main_rig_geometry_line_edit.setReadOnly(True)
        self.main_rig_geometry_line_edit.textChanged.connect(lambda: self.updateRigMainGeometry(self.main_rig_geometry_line_edit.text()))
        self.main_rig_geometry_line_edit.textChanged.connect(lambda: self.scene.setModified(True))

        self.main_rig_geometry_setter_button = QtWidgets.QPushButton("Set")
        self.main_rig_geometry_setter_button.clicked.connect(self.setRigMainGeometry)
        self.main_rig_geometry_clear_button = QtWidgets.QPushButton("Clear")

        self.main_rig_geometry_layout.addWidget(self.main_rig_geometry_line_edit)
        self.main_rig_geometry_layout.addWidget(self.main_rig_geometry_setter_button)
        self.main_rig_geometry_layout.addWidget(self.main_rig_geometry_clear_button)

        self.layout.addLayout(self.main_rig_geometry_layout)

        #define additional Rig Geometry

    def initActions(self):
        self.action_layout = QtWidgets.QHBoxLayout()

        self.build_guides_action_button = QtWidgets.QPushButton("Build Guides")
        self.build_guides_action_button.clicked.connect(self.onBuildGuides)

        self.build_static_action_button = QtWidgets.QPushButton("Build Static")
        self.build_static_action_button.clicked.connect(self.onBuildStatic)

        self.build_component_action_button = QtWidgets.QPushButton("Build")
        self.build_component_action_button.clicked.connect(self.onBuildComponent)

        self.connect_component_action_button = QtWidgets.QPushButton("Connect")
        self.connect_component_action_button.clicked.connect(self.onConnectComponents)

        self.action_layout.addWidget(self.build_guides_action_button)
        self.action_layout.addWidget(self.build_static_action_button)
        self.action_layout.addWidget(self.build_component_action_button)
        self.action_layout.addWidget(self.connect_component_action_button)

        self.layout.addLayout(self.action_layout)

        self.setLayout(self.layout)

    def updateRigName(self, text):
        self.rig_name = text
    
    def updateRigMainGeometry(self, text):
        self.rig_main_geometry = text

    def getRigName(self):
        return self.rig_name

    def getRigMainGeometry(self):
        return self.rig_main_geometry

    def setRigMainGeometry(self):
        self.main_rig_geometry_line_edit.setText(MC.getFirstInViewPortSelection())

    def onBuildGuides(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onBuildGuides:: Building Guides!")

    def onBuildStatic(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onBuildStatic:: Building Static")

    def onBuildComponent(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onBuildComponent:: Building Component ")

    def onConnectComponents(self):
        if EVENT_DEBUG: print("PROPERTIES:: --onConnectComponents:: Connecting Components")

    def serialize(self):
        result_data = super().serialize()
        result_data['rig_name'] = self.rig_name
        result_data['rig_main_geometry'] = self.rig_main_geometry
        return result_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True):
        result = super().deserialize(data, hashmap, restore_id)

        self.rig_name_line_edit.setText(data['rig_name'])
        self.main_rig_geometry_line_edit.setText(data['rig_main_geometry'])