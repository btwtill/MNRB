from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore

from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore
log = ROSE_Log.get("rose.components.guides")

class LocatorUpGuideShape():
    def __init__(self, guide) -> None:
        self.guide = guide

    def draw(self):
        log.debug("%s::draw::UpShape Name::" % self.__class__.__name__, self.guide.name_up)
        guide_shape = MC.createSpaceLocator(self.guide.position, self.guide.name_up, self.guide.color.value)
        log.debug("%s::draw::UpShape Name::After Creation::" % self.__class__.__name__, guide_shape)
        self.guide.name_up = guide_shape

    def resize(self, size):
        MC.setLocatorLocalScale(self.guide.name_up, size)

    def updateColor(self):
        MC.setObjectDisplayColor(self.guide.name_up, self.guide.color.value)
