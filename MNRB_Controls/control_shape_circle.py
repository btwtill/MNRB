from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore 

class control_shape_circle():
    def __init__(self, control):
        self.control = control

    def draw(self):
        print("Drawing control Shape Circle.")
        self.control.name = MC.createNurbsCircle(self.control.name)

    def resize(self):
        print("Resizeing control Shape Circle")