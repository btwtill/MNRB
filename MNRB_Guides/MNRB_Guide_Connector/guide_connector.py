from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore

CLASS_DEBUG = True

class Guide_Connector():
    def __init__(self, start_guide, end_guide):
        
        self.guide = end_guide

        self._start_guide = None
        self._end_guide = None
        self._name = None

        self.start_guide = start_guide
        self.end_guide = end_guide

        self.name = self.guide.name + MNRB_Names.guide_connector_suffix

    @property
    def start_guide(self): return self._start_guide
    @start_guide.setter
    def start_guide(self, value):
        if CLASS_DEBUG: print("%s::setting start Guide to: " % self.__class__.__name__, value)
        self._start_guide = value

    @property
    def end_guide(self): return self._end_guide
    @end_guide.setter
    def end_guide(self, value):
        if CLASS_DEBUG: print("%s::setting end Guide to: " % self.__class__.__name__, value)
        self._end_guide = value

    @property
    def name(self): return self._name
    @name.setter
    def name(self, value):
        self._name = value

    def initUI(self):
        if CLASS_DEBUG: print("%s::initUI " % self.__class__.__name__)

    def build(self):
        if CLASS_DEBUG: print("%s::build " % self.__class__.__name__)
        if self.exists():
            self.remove()
        self.name = MC.createTransform(self.name)
        MC.parentObject(self.name, self.guide.node.guide_component_hierarchy)

    def remove(self):
        if CLASS_DEBUG: print("%s::remove " % self.__class__.__name__)
        if self.exists():
            MC.deleteNode(self.name)

    def updateColor(self):
        if CLASS_DEBUG: print("%s::updateColor " % self.__class__.__name__)
    
    def update(self):
        if CLASS_DEBUG: print("%s::update " % self.__class__.__name__)
    
    def exists(self):
        if MC.objectExists(self.name): return True
        else: return False