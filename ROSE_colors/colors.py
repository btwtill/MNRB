from enum import Enum
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_naming.ROSE_names import ROSE_Names #type: ignore

class ROSEColor(Enum):
    #Saved by name, so members can be added and reordered freely but never
    #renamed. Every value has to be unique: Enum turns a member with a repeated
    #value into an alias of the first, and it would vanish from the dropdown.
    yellow = (1,1,0)
    red = (1,0,0)
    green = (0,1,0)
    blue = (0,0,1)

    orange = (1.0, 0.5, 0.0)
    gold = (1.0, 0.8, 0.2)
    darkRed = (0.6, 0.0, 0.0)
    pink = (1.0, 0.45, 0.7)
    magenta = (1.0, 0.0, 1.0)
    purple = (0.55, 0.2, 1.0)
    lightBlue = (0.35, 0.65, 1.0)
    cyan = (0.0, 1.0, 1.0)
    teal = (0.0, 0.6, 0.55)
    lime = (0.6, 1.0, 0.1)
    brown = (0.55, 0.3, 0.1)
    white = (1.0, 1.0, 1.0)
    grey = (0.5, 0.5, 0.5)

class ROSESceneColors():
    def __init__(self, scene) -> None:
        self.scene = scene

        self.color_material_names = []
        self.color_shader_name = []

        self.initColors()
        self.initMaterials()

    def initColors(self):
        for color in ROSEColor:
            self.color_material_names.append(color.name + ROSE_Names.guide_material_suffix)
            self.color_shader_name.append(color.name + ROSE_Names.guide_shader_suffix)

    def initMaterials(self):
        for index, color in enumerate(ROSEColor):
            is_connected = True
            if not MC.objectExists(self.color_material_names[index]):
                MC.createLambertMaterial(self.color_material_names[index])
                #configure Material
                MC.setLambertColor(self.color_material_names[index], color.value)
                MC.setLambertTransparency(self.color_material_names[index], (0.2, 0.2, 0.2))
                MC.setLambertAmbientColor(self.color_material_names[index], (1.0, 1.0, 1.0))
                MC.setLambertIncandescence(self.color_material_names[index], (0.2, 0.2, 0.2))
                is_connected = False

            if not MC.objectExists(self.color_shader_name[index]):
                #create shader
                MC.createShaderSet(self.color_shader_name[index])
                #connect material node to shader
                MC.assignMaterialToShaderSet(self.color_material_names[index], self.color_shader_name[index])
                is_connected = True
            
            if not is_connected:
                MC.assignMaterialToShaderSet(self.color_material_names[index], self.color_shader_name[index])

    def removeAllMaterials(self):
        for node in (self.color_material_names + self.color_shader_name):
            if MC.objectExists(node):
                MC.deleteNode(node)

    @staticmethod
    def mapColorNameToColor(color_name):
        exception_color = ROSEColor.yellow
        for color in ROSEColor:
            if color_name == color.name:
                return color
        
        return exception_color