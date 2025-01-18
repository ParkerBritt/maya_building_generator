import maya.cmds as cmds
import math
import random

class Ball:
    def __init__(self, scene_data, stairs, name="ball", radius=1.0, x=0.0, y=0.0, z=0.0, frame_step=8):
        print("ball constructor")

        self.name = name
        self.radius = radius

        self.stairs = stairs
        self.scene_data = scene_data

        # position
        self.x_pos = x
        self.y_pos = y
        self.z_pos = z+math.pi/2*self.scene_data.STEP_DEPTH

        self.BOUNCE_HEIGHT = 300 # how many units to move up
        self.BOUNCE_ANGLE = -20 # how much to lean when jumping

        self.SQUASH_MULT = 0.6 # multiply base scale
        self.STRETCH_MULT = 1.3 # multiply base scale
        self.SQUASH_TIME = 2 # frames

        # how many frames to leave between starting the jump and mid jump
        self.FRAME_STEP = frame_step

        # cleanup objects from previous run
        self.cleanUp()

        # create ball
        self.name = cmds.polySphere(name=self.name, radius=self.radius)[0]

        # set keyframes on ball
        self.createKeyFrames()

    # cleanup objects from previous run
    def cleanUp(self):
        if(cmds.objExists(self.name)):
            print("deleting object:", self.name)
            cmds.delete(self.name)

    def createKeyFrames(self):
        print("creating keyframes")
        iterations = 100 # how many steps the ball will climb
        for i in range(iterations):

            # current step
            step_number = math.floor(i)%len(self.stairs.step_objects)
            step = self.stairs.step_objects[step_number]
            next_step = self.stairs.step_objects[(step_number+1)%len(self.stairs.step_objects)]

            # current frame
            frame = i*self.FRAME_STEP*2+random.randint(-1,1)

            bounce_height = max(next_step.topY-step.topY+self.BOUNCE_HEIGHT, self.BOUNCE_HEIGHT)

            # set pos
            self.x_pos = step.posX
            self.z_pos = step.posZ+random.uniform(-0.5, 0.5) *step.scaleZ/2
            # self.y_pos += (not i == 0)*self.scene_data.STEP_VERT_OFFSET
            self.y_pos = self.radius+step.topY

            # ground
            cmds.setKeyframe(self.name, time=frame, attribute="rotateX", value=0)
            cmds.setKeyframe(self.name, time=frame, attribute="rotateY", value=step.rotY)
            cmds.setKeyframe(self.name, time=frame, attribute="translateY", value=self.y_pos)
            cmds.setKeyframe(self.name, time=frame, attribute="translateX", value=self.x_pos)
            cmds.setKeyframe(self.name, time=frame, attribute="translateZ", value=self.z_pos)
            cmds.setKeyframe(self.name, time=frame, attribute="scaleY", value=1)
            cmds.setKeyframe(self.name, time=frame, attribute="scaleX", value=1)
            cmds.setKeyframe(self.name, time=frame, attribute="scaleZ", value=1)
            cmds.setKeyframe(self.name, time=frame, attribute="rotateZ", value=0)

            # squash
            cmds.setKeyframe(self.name, time=frame+self.SQUASH_TIME, attribute="rotateX", value=-self.BOUNCE_ANGLE)
            cmds.setKeyframe(self.name, time=frame+self.SQUASH_TIME, attribute="translateY", value=self.y_pos-self.radius*self.SQUASH_MULT)
            cmds.setKeyframe(self.name, time=frame+self.SQUASH_TIME, attribute="translateX", value=self.x_pos)
            cmds.setKeyframe(self.name, time=frame+self.SQUASH_TIME, attribute="translateZ", value=self.z_pos)
            cmds.setKeyframe(self.name, time=frame+self.SQUASH_TIME, attribute="scaleY", value=self.SQUASH_MULT)
            cmds.setKeyframe(self.name, time=frame+self.SQUASH_TIME, attribute="scaleX", value=1/math.sqrt(self.SQUASH_MULT))
            cmds.setKeyframe(self.name, time=frame+self.SQUASH_TIME, attribute="scaleZ", value=1/math.sqrt(self.SQUASH_MULT))
            cmds.setKeyframe(self.name, time=frame+self.SQUASH_TIME, attribute="rotateZ", value=0)

            # unsquash
            cmds.setKeyframe(self.name, time=frame+4, attribute="scaleY", value=1)
            cmds.setKeyframe(self.name, time=frame+4, attribute="scaleX", value=1)
            cmds.setKeyframe(self.name, time=frame+4, attribute="scaleZ", value=1)

            # stretch
            cmds.setKeyframe(self.name, time=frame+8, attribute="scaleY", value=self.STRETCH_MULT)
            cmds.setKeyframe(self.name, time=frame+8, attribute="scaleX", value=1/math.sqrt(self.STRETCH_MULT))
            cmds.setKeyframe(self.name, time=frame+8, attribute="scaleZ", value=1/math.sqrt(self.STRETCH_MULT))

            # mid bounce
            cmds.setKeyframe(self.name, time=frame+self.FRAME_STEP, attribute="translateY", value=self.y_pos+bounce_height)

            # rotate for land
            cmds.setKeyframe(self.name, time=frame+self.FRAME_STEP+self.SQUASH_TIME, attribute="rotateX", value=self.BOUNCE_ANGLE/2)


