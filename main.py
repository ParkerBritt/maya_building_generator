from importlib import reload
import math
import maya.cmds as cmds
import maya.utils
import pymel.core as pm
import random
from PySide2 import QtWidgets

# import other packages
import package.stairs
import package.ball
import package.scene_data
import package.camera
import package.building.window
import package.building.building_gen
import package.building.user_vars
# reload packages
reload(package.stairs)
reload(package.ball)
reload(package.scene_data)
reload(package.camera)
reload(package.building.window)
reload(package.building.building_gen)
reload(package.building.user_vars)
# reimport after reload
from package.stairs import Stairs
from package.ball import Ball
from package.scene_data import SceneData
from package.camera import Camera
from package.building.window import Window
from package.building.building_gen import BuildingGen
from package.building.user_vars import UserVars

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QLabel, QProgressBar, QVBoxLayout, QWidget
from maya import OpenMayaUI as omui 
from shiboken2 import wrapInstance

class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.setWindowFlags(Qt.Window)

        main_layout.addWidget(QLabel("Loading Progress..."))
        progress_bar = QProgressBar()
        main_layout.addWidget(progress_bar)



import time
def main():
    print("\n\n\n\n\n\n\n\n\n\n-------new--------")
    # init loading
    start_time = time.time()
    loading_amount = 0

    # setup scene data
    scene_data = SceneData()

    scene_data.STEP_HEIGHT =  1200
    scene_data.STEP_VERT_OFFSET = 50
    scene_data.STEP_DEPTH = 600
    scene_data.STEP_WIDTH = 1000
    scene_data.BALL_DIAMETER = 200
    scene_data.BALL_RADIUS = scene_data.BALL_DIAMETER/2

    # start pos
    ball_x = 0.0
    ball_y = scene_data.BALL_RADIUS+scene_data.STEP_HEIGHT/2
    ball_z = 0.0

    # cleanup scene
    # if(cmds.objExists("scene")):
    #     print("deleting previous scene")
    #     cmds.delete("scene")

    if(False):
        selection = pm.general.ls(selection=True)
        print("selection:", selection)
        BuildingGen(selection[0].fullPath(), selected_faces = None)
        return

    pm.progressWindow(    title="Loading",
                                        progress=loading_amount,
                                        status="Init: 0%",
                                        isInterruptable=True )

    # create scene
    scene_grp = cmds.group(empty=True, name="scene")
    # create scene objects
    # cmds.parent(window.grp, scene_grp)
    stairs = Stairs(scene_data)
    # cmds.parent(stairs.grp_name, scene_grp)

    color_set = (
        # (1.000, 0.640, 0.588),   # pink
        (0.583,0.518,0.447),     # dark brown
        (0.838,0.727,0.527),     # light tan
        (0.780,0.564,0.361),     # orange
        (1.000, 0.959, 0.765),   # very light yellow
    )

    shader_set = (
        "stucco_white",
        "bricks_color",
        "aerated_concrete_block_wall",
    )

    roof_shader_set = (
        "roof_01",
        "roof_02",
    )


    color = color_set[random.randint(0, len(color_set)-1)]

    color_variation = 0.04
    color_batch_indx = 0
    color_batch_max = 4
    buildings_group = pm.group(em=True, name="Buildings")

    try:
        for i, step in enumerate(stairs.step_objects):
            has_corner_decor = random.uniform(0,1)>0.5
            edge_bevel_amount = (not has_corner_decor)*7
            edge_bevel_amount = 0

            if(random.uniform(0,1)>0.7 or color_batch_indx > color_batch_max):
                color_batch_indx = 1
                color = color_set[random.randint(0, len(color_set)-1)]
            else:
                color_batch_indx+=1

            if(step.is_corner):
                occluded_faces = [5,0]
            else:
                occluded_faces = [5,0,2]


            user_variables = {
                    UserVars.OCCLUDED_FACES: occluded_faces,

                    UserVars.HAS_CORNER_DECOR:has_corner_decor,
                    UserVars.CORNER_BRICK_HEIGHT:random.uniform(0.4, 2),
                    UserVars.CORNER_ALT_WIDTH:random.uniform(0.5, 1),
                    UserVars.CORNER_BRICK_GAP:random.uniform(0, 3),

                    UserVars.FLOOR_TRIM_HEIGHT:random.uniform(0.9,3),
                    UserVars.ROOF_TRIM_VERT_SCALE:random.uniform(0.5, 3),

                    UserVars.EDGE_BEVEL_AMOUNT:edge_bevel_amount,
                    UserVars.FLOOR_DENSITY:random.uniform(0.6,1),
                    UserVars.COLOR_WALL:(color[0]+random.uniform(-color_variation/2, color_variation/2), color[1]+random.uniform(-color_variation/2, color_variation/2), color[2]+random.uniform(-color_variation/2, color_variation/2)),
                    UserVars.SHADER_NAME:shader_set[random.randint(0, len(shader_set)-1)],

                    UserVars.ROOF_SHADER:roof_shader_set[random.randint(0, len(roof_shader_set)-1)],
                    UserVars.GROUND_FLOOR_HEIGHT:random.uniform(300, 450),
                    UserVars.BOTTOM_BULKHEAD_VERT_SCALE:random.uniform(0.5, 1.5),
                }
            building = BuildingGen(step.name, user_variables)
            pm.parent(building.group, buildings_group)

            # handle loading
            elapsed_time = time.time()-start_time
            loading_amount = round(i/len(stairs.step_objects)*100)
            if pm.progressWindow( query=True, isCancelled=True ) :
                break
            if pm.progressWindow( query=True, isCancelled=True ) :
                break
            pm.progressWindow( edit=True, progress=loading_amount, status=f"Creating Building: {i}\nElapsed Time: {elapsed_time:.2f}s" )
            # pm.refresh() # refresh everything but slower than process events
            QtWidgets.QApplication.processEvents()
            # break

        ball = Ball(scene_data, stairs, radius=scene_data.BALL_RADIUS, x=ball_x, y=ball_y, z=ball_z)
        # # camera = Camera()
        pm.progressWindow(endProgress=1) # end progress bar
    except:
        pm.progressWindow(endProgress=1) # end progress bar
        raise


