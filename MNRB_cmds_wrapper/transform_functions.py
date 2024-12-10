import MNRB.MNRB_cmds_wrapper.cmds_wrapper as wrapper #type: ignore

class Transform_functions():
    @staticmethod
    def connectSrt(source, target, translate = True, rotate = True, scale = True, rotate_order = True):
        for channel in "XYZ":
            if translate:
                wrapper.MC.connectAttribute(source, "translate" + channel, target , "translate" + channel)
            if rotate:
                wrapper.MC.connectAttribute(source, "rotate" + channel, target , "rotate" + channel)
            if scale:
                wrapper.MC.connectAttribute(source, "scale" + channel, target , "scale" + channel)
        if rotate_order:
            wrapper.MC.connectAttribute(source, "rotateOrder", target, "rotateOrder")