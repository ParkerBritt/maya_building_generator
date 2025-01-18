import pymel.core as pm
import maya.cmds as cmds
import math
import random

class Stairs:
    def __init__(self, scene_data):
        print("stairs constructor")

        self.scene_data = scene_data

        self.grp_name = "stairs"
        self.step_objects = []

        self.RAND_HEIGHT_VARIANCE = 1
        
        self.center_offset = 10
        self.radius = self.center_offset+self.scene_data.STEP_WIDTH
        self.circumference = 2*math.pi*self.radius

        self.cleanUp()
        self.createStairs()

    # cleanup objects from previous run
    def cleanUp(self):
        if(cmds.objExists(self.grp_name)):
            print("deleting object:", self.grp_name)
            cmds.delete(self.grp_name)


    def sign(self, num):
        if num > 0:
            return 1
        elif num < 0:
            return -1
        else:
            return 0

    def createStairs(self):
        self.step_cnt = 40
        radius = 10

        # set up how many steps are on each side
        steps_per_side = (8,10,4,6)

        total_steps = sum(steps_per_side)
        print("total_steps", total_steps)

        IS_FLOATING = False

        x_pos = 0
        z_pos = 0
        rot_y = 90
        current_side = 0
        for side in range(len(steps_per_side)):
            side_step_cnt = steps_per_side[side]
            if side>1:
                flip = -1
            else:
                flip = 1

            print("flip:", flip)

            for i in range(side_step_cnt):
                current_step = sum(steps_per_side[:side])+i
                print("current step", current_step)
                step_width = self.scene_data.STEP_WIDTH
                step_depth = self.scene_data.STEP_DEPTH
                step_height = self.scene_data.STEP_HEIGHT

                if(i!=0 and i!=side_step_cnt-1):
                    step_width *= random.uniform(0.9, 1.2)


                scaleX = step_width
                scaleY = step_height
                scaleZ = step_depth

                if(i==0): # corner step
                    scaleZ = step_width
                if(i==1):
                    if(side%2==0):
                        x_pos += -step_depth/2*flip+step_width/2*flip
                    else:
                        z_pos += -step_depth/2*flip+step_width/2*flip


                # y position increases for each step based on vertical offet
                y_pos = current_step*self.scene_data.STEP_VERT_OFFSET

                # adjust height and offset if not floating
                if(not IS_FLOATING):
                    scaleY += current_step*self.scene_data.STEP_VERT_OFFSET
                    y_pos/=2

                # random scale variation
                random_height_offset = random.randrange(0, self.RAND_HEIGHT_VARIANCE+1)
                scaleY += random_height_offset
                y_pos += random_height_offset/2

                if(side == 0 and i < 5):
                    mod = 1600 
                    scaleY+=mod
                    y_pos-=mod/2

                # create new stair object
                print("creating step:", x_pos, z_pos)
                new_step = Step(self.scene_data,
                                x=x_pos,
                                y=y_pos,
                                z=z_pos,
                                rot_y=rot_y,
                                scaleX=scaleX,
                                scaleY=scaleY,
                                scaleZ=scaleZ
                                )

                if(i==0): # corner step
                    new_step.is_corner = True 
                    cmds.polyBevel(new_step.name+".e[9]", offset = 1*step_depth)


                # flip opposite steps
                if(i!=steps_per_side[side]-1):
                    if(side%2==0):
                        x_pos += step_depth*flip
                    else:
                        z_pos += step_depth*flip
                else:
                    if(side%2==0):
                        x_pos += (step_depth/2+step_width/2)*flip
                    else:
                        z_pos += (step_depth/2+step_width/2)*flip


                self.step_objects.append(new_step)

            # rotate 90 degrees after each stair section
            rot_y -= 90

        # groups steps
        # cmds.group(*[step.name for step in self.step_objects], name=self.grp_name)

class Step:
    def __init__(self,
                 scene_data,
                 name="step",
                 x=0,
                 y=0,z=0,
                 rot_y=0,
                 scaleX=1,
                 scaleY=1,
                 scaleZ=1,
                 ):
        self.scene_data = scene_data
        self.is_corner = False

        # create cube and set name to new cube
        self.name = cmds.polyCube(depth=scaleZ,
                                  height=scaleY,
                                  width=scaleX,
                                  name=name
                                  )[0]
        self.node = pm.PyNode(self.name)


        self.posX = x
        self.posY = y
        self.posZ = z

        self.scaleX = scaleX
        self.scaleY = scaleY
        self.scaleZ = scaleZ

        self.topY = self.posY+scaleY/2

        self.rotY = rot_y

        cmds.setAttr(self.name+".translateX", x)
        cmds.setAttr(self.name+".translateY", y)
        cmds.setAttr(self.name+".translateZ", z)

        cmds.setAttr(self.name+".rotateY", rot_y)
