from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore

CLASS_DEBUG = True

class MultiEdit_PropertyWidget(MNRB_NodeProperties):
    def __init__(self, graphic_nodes = [], parent = None):
        super().__init__(graphic_nodes[0].node)

        self.nodes = []
        for graphic_node in graphic_nodes:
            self.nodes.append(graphic_node.node)

        self.title = "Multi Edit Properties"

        if CLASS_DEBUG: print("%s:: MultiEdit_PropertyWidget:: __init__:: " % self.__class__.__name__)
        if CLASS_DEBUG: 
            for node in self.nodes:
                print("%s:: Nodes contained in the multie Edit:: " % self.__class__.__name__, node)

    def updateGuideSize(self):
        self.guide_size = float(self.guide_slider_size_edit.text())
        if CLASS_DEBUG: print("%s:: --updateGuideSize:: Setting Guide Size To: " % self.__class__.__name__, self.guide_size, " of Node:: self.node")
        for node in self.nodes:
            node.setComponentGuideSize(self.guide_size)
            node.properties.guide_slider_size_edit.setText(str(self.guide_size))
            node.properties.guide_size = self.guide_size
        self.setHasBeenModified()

    def updateDeformSize(self):
        self.deform_size = float(self.deform_slider_size_edit.text())
        if CLASS_DEBUG: print("%s:: --updateDeformSize:: Setting Deform Size To: " % self.__class__.__name__, self.deform_size)
        if CLASS_DEBUG: print("%s:: --updateDeformSize:: of Node::  " % self.__class__.__name__, self.node)
        for node in self.nodes:
            node.setComponentDeformRadius(self.deform_size)
            node.properties.deform_slider_size_edit.setText(str(self.deform_size))
            node.properties.deform_size = self.deform_size
        self.setHasBeenModified()

    def updateControlSize(self):
        self.control_size = float(self.control_slider_size_edit.text())
        if CLASS_DEBUG: print("%s:: --updatecontrolSize:: Setting control Size To: " % self.__class__.__name__, self.control_size)
        if CLASS_DEBUG: print("%s:: --updatecontrolSize:: of Node::  " % self.__class__.__name__, self.node)
        for node in self.nodes:
            node.setComponentControlsSize(self.control_size)
            node.properties.control_slider_size_edit.setText(str(self.control_size))
            node.properties.control_size = self.control_size
        self.setHasBeenModified()

    def onBuildGuides(self):
        if CLASS_DEBUG: print("BaseNodeProperties:_ --onBuildGuides ", self.node)
        if not self.is_disabled:
            for node in self.nodes:
                node.guideBuild()

    def onBuildStatic(self):
        if CLASS_DEBUG: print("BaseNodeProperties:_ --onBuildStatic ", self.node)
        if not self.is_disabled:
            for node in self.nodes:
                node.staticBuild()

    def onBuildComponent(self):
        if CLASS_DEBUG:  print("BaseNodeProperties:: --onBuildComponent: ", self.node)
        if not self.is_disabled:
            for node in self.nodes:
                node.componentBuild()

    def onConnectComponents(self):
        if CLASS_DEBUG: print("BaseNodeProperties:: --onConnectComponent: ", self.node)
        if not self.is_disabled:
            for node in self.nodes:
                node.connectComponent()