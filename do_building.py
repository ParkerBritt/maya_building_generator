import pymel.core as pm

from importlib import reload
import package.building.building_gen
reload(package.building.building_gen)
from package.building.building_gen import BuildingGen

def main():
    selection = pm.general.ls(selection=True)
    print("selection:", selection)
    for selection_item in selection:
        BuildingGen(selection_item.fullPath(), selected_faces = None)
