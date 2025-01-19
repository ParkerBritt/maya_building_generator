import pymel.core as pm

from importlib import reload
import maya_building_generator.building.building_gen
reload(maya_building_generator.building.building_gen)
from maya_building_generator.building.building_gen import BuildingGen

def main():
    selection = pm.general.ls(selection=True)
    print("selection:", selection)
    for selection_item in selection:
        BuildingGen(selection_item.fullPath(), selected_faces = None)
