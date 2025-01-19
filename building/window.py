import maya.cmds as cmds

class Window():
    def __init__(self):
        print("Window Constructor")

        self.name = "window"
        self.objects = []
        self.height = 3
        self.width = 1

        self.grp = None
        self.create()

    def createCube(self, _name, _pos=(0,0,0), _scale=(1,1,1), _floor=True, _z_flush=0):
        name = cmds.polyCube(name=_name, width=_scale[0], height=_scale[1], depth=_scale[2])[0]
        cmds.setAttr(name+".translateY", _pos[1]+_scale[1]/2*_floor)
        cmds.setAttr(name+".translateZ", _pos[2]+_scale[2]/2*_z_flush)
        self.objects.append(name)
        return name

    def create(self):
        # pane = cmds.polyCube(name="pane", width=1, height=3, depth=0.1)[0]
        # self.objects.append(pane)

        self.createCube("pane", _scale=(1.5,2.5,0.01), _z_flush=1)
        
        self.grp = cmds.group(self.objects, name="window")

