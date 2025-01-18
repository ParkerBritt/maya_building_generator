import maya.cmds as cmds

class Camera():
    def __init__(self):
        print("Camera Constructor")
        self.cameraName = "RenderCam1"
        self.cleanup()
        self.create()

    
    def cleanup(self):
        if(cmds.objExists(self.cameraName)):
            print("deleting object:", self.cameraName)
            cmds.delete(self.cameraName)
    
    def create(self):
        self.cameraName = cmds.camera(
                name = self.cameraName,
                orthographic=True,
                rot=(-20,45,0),
                position=(17,6,17)
                )[0]

