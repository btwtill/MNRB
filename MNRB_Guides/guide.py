from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class guide():
    def __init__(self, name, color = "#FF0000", position = (0, 0, 0), size = 1) -> None:
       
        self.name = name
        self.color = color

        self.position = position
        self.size = 1

    def draw(self):
        MC.createSpaceLocator(self.position)