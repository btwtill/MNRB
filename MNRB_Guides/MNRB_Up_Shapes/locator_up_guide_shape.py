from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

CLASS_DEBUG = False

class LocatorUpGuideShape():
    def __init__(self, guide) -> None:
        self.guide = guide

    def draw(self):
        if CLASS_DEBUG: print("%s::draw::UpShape Name::" % self.__class__.__name__, self.guide.name_up)
        guide_shape = MC.createSpaceLocator(self.guide.position, self.guide.name_up, self.guide.color.value)
        if CLASS_DEBUG: print("%s::draw::UpShape Name::After Creation::" % self.__class__.__name__, guide_shape)
        self.guide.name_up = guide_shape

    def resize(self, size):
        MC.setLocatorLocalScale(self.guide.name_up, size)

    def updateColor(self):
        MC.setObjectDisplayColor(self.guide.name_up, self.guide.color.value)
