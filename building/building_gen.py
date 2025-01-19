import maya.cmds as cmds
import pymel.core as pm
import math
import random
from importlib import reload

import maya_building_generator.building.user_vars
import maya_building_generator.building.building_side
reload(maya_building_generator.building.user_vars)
reload(maya_building_generator.building.building_side)
from maya_building_generator.building.user_vars import UserVars
from maya_building_generator.building.building_side import BuildingSide


class BuildingGen():
    """Handle geometry and shader operations to convert a primitive geometry into a building"""
    def __init__(self, _reference_cube_path, user_variables={}, selected_faces=None):
        """Setup prerequisite data structures and variables"""
        self.group = pm.group(em=True, name="Building")

        # user variables
        self.user_variables = {
                UserVars.CORNERS_ONLY:False,

                UserVars.HAS_CORNER_DECOR:True,
                UserVars.GROUND_FLOOR_HEIGHT:400,
                UserVars.CORNER_ALT_WIDTH:0.6,
                UserVars.CORNER_BRICK_HEIGHT:1,
                UserVars.CORNER_BRICK_GAP:0,

                UserVars.FLOOR_TRIM_HEIGHT:1,
                UserVars.ROOF_TRIM_VERT_SCALE:1,

                UserVars.OCCLUDED_FACES:None,
                UserVars.EDGE_BEVEL_AMOUNT:0,
                UserVars.FLOOR_DENSITY:1,

                UserVars.COLOR_WALL:None,
                UserVars.SHADER_NAME:None,

                UserVars.ROOF_SHADER:None,
                UserVars.BOTTOM_BULKHEAD_VERT_SCALE:1,
        }
        self.user_variables.update(user_variables)

        self.occluded_faces = self.user_variables[UserVars.OCCLUDED_FACES]
        print("reference cube path:", _reference_cube_path)
        self.reference_cube = pm.PyNode(_reference_cube_path)
        self.reference_cube_shape = self.reference_cube.getShape()
        self.height = self.reference_cube.boundingBox().height()

        bulkhead_names = ["bottom_bulkead_01", "bottom_bulkead_02", "bottom_bulkead_03"]
        self.bottom_bulkhead_geo = pm.PyNode(bulkhead_names[random.randint(0, len(bulkhead_names)-1)])

        if(self.user_variables[UserVars.EDGE_BEVEL_AMOUNT]>0):
            print("beveling edges")
            bevel_return = pm.modeling.polyBevel(self.reference_cube.edges, offset=self.user_variables["edge_bevel_amount"])
            print("BEVEL RETURN VAL:", bevel_return, type(bevel_return))


        # select input faces
        self.input_faces = []
        self.roof_faces = []
        if(selected_faces == None):
            self.input_faces = self.get_faces()
        else:
            for i in selected_faces:
                self.input_faces.append(self.reference_cube.faces[i])

        # bake corner decor
        self.corner_piece = self.bake_corner_decor()
        # pm.parent(self.corner_piece, self.group)

        self.inset_roof()
        self.assign_wall_shader()

        # create building sides
        self.building_sides = []
        self.populate_sides() # place geometry on each side of the building
        pm.general.delete(self.corner_piece) # clean up reference piece
        pm.parent(self.reference_cube, self.group)

        # set wall colors
        self.set_wall_color()


        # project uvs (same parameters as UV->automatic button)
        pm.polyAutoProjection(
            self.reference_cube_shape,
            caching=1,
            lm=0,
            pb=0,
            ibd=1,
            cm=0,
            l=2,
            sc=1,
            o=1,
            p=6,
            ps=0.2,
            ws=0,
        )


    def inset_roof(self):
        """Extrude face inwards and down"""
        print("roof faces:", self.roof_faces)
        pm.polyExtrudeFacet(self.roof_faces, offset= 20)
        pm.polyExtrudeFacet(self.roof_faces, thickness=-20.0)

    def assign_wall_shader(self):
        """Assign shader to wall"""
        shader_name = self.user_variables[UserVars.SHADER_NAME]
        if(shader_name is None):
            shader_name = "stucco_white"
        pm.select(self.reference_cube_shape)
        pm.hyperShade(assign = shader_name)
        self.set_roof_color()
        

    def set_wall_color(self):
        """Set Color Attribute on wall geometry for shader to read"""
        # available colors to pick from
        color_set = (
            (1.000, 0.640, 0.588),   # pink
            (0.583,0.518,0.447),     # dark brown
            (0.838,0.727,0.527),     # light tan
            (0.780,0.564,0.361),     # orange
            # (0.457,0.315,0.226),     # dark brown saturated
            (1.000, 0.959, 0.765),   # very light yellow
        )

        # user provided wall color
        wall_color = self.user_variables[UserVars.COLOR_WALL]
        # if user does not choose a color, pick a random color from the set
        if(wall_color is None):
            wall_color = color_set[random.randint(0, len(color_set)-1)]
        print("setting color:", wall_color)


        # set color attribute
        if(not pm.general.hasAttr(self.reference_cube_shape, "mtoa_constant_color")):
            print("no color attribute on mesh, creating one now")
            pm.general.addAttr(self.reference_cube_shape, ln="mtoa_constant_color", type="float3", usedAsColor=1)
        else:
            print("mesh already has a color attribute, skipping creation")
        pm.general.setAttr(self.reference_cube_shape.fullPath()+".mtoa_constant_color", *wall_color)




    def set_roof_color(self):
        """Set color attribute on roof"""
        # assign roof shader
        roof_shader_name = self.user_variables[UserVars.ROOF_SHADER]
        if(roof_shader_name is None):
            roof_shader_name = "roof_01"
        pm.select(*self.roof_faces)
        pm.hyperShade(assign = roof_shader_name)


    def bake_corner_decor(self):
        """Bake a single column of the corner bricks at the corrent height to be instanced later on each corner"""
        self.corner_geo_list = []
        instance_geo = pm.PyNode("corner_brick")
        instance_bbox = instance_geo.boundingBox()
        alternate_width = self.user_variables[UserVars.CORNER_ALT_WIDTH]

        gap = self.user_variables[UserVars.CORNER_BRICK_GAP]
        decor_height = (instance_bbox.height()+gap)
        decor_height *= self.user_variables[UserVars.CORNER_BRICK_HEIGHT]

        corner_decor_cnt = math.floor((self.height)/decor_height)

        for j in range(0, corner_decor_cnt):
            corner_decor = pm.general.duplicate(instance_geo)
            x = 0
            hor_scale = 1
            vert_scale = self.user_variables[UserVars.CORNER_BRICK_HEIGHT]
            # scale every other down by alternate_width
            if(j%2==0):
                hor_scale = alternate_width
                x=(instance_bbox.width()-instance_bbox.width()*alternate_width)/2
                            # scale uvs


            corner_decor[0].scaleBy((hor_scale,vert_scale,1))

            uvs = corner_decor[0].map[:]
            pm.select(uvs)
            pm.polyEditUV(scaleU=hor_scale, scaleV=vert_scale)

            y=j*(decor_height)
            corner_decor[0].translateBy((x,y,0))

            self.corner_geo_list.append(corner_decor)

        baked_corner = pm.modeling.polyUnite(*self.corner_geo_list, constructionHistory=False)

        # assign shader
        pm.select(baked_corner)
        pm.hyperShade(assign = "white_concrete")
        # pm.parent(baked_corner, self.group)

        return baked_corner


    def get_faces(self):
        """Create and store a face object for each side face on the geomtry"""
        faces = []
        for i, face in enumerate(self.reference_cube.faces):
            # skip top and bottom faces
            normal = face.getNormal(space="world")
            if(abs(normal.dot({0,1,0}))>0.9):
                self.roof_faces.append(face)
                continue

            # skip angled (for bevel)
            if(normal.y!=0):
                continue

            # skip faces that are too small
            min_edge_len = 3
            face_edges = face.getEdges()
            is_large_enough = True
            for edge_indx in face_edges:
                edge = pm.general.MeshEdge(face, edge_indx)
                edge_length = edge.getLength()
                if(edge_length<min_edge_len):
                    print("face too small, skipping", face)
                    is_large_enough = False
            if(not is_large_enough):
                continue
            
            faces.append(face)

        return faces



    def populate_sides(self):
        """Populate the each side with instance geometry"""
        for face in self.input_faces:
            corners_only = self.occluded_faces and face.index() in self.occluded_faces
            self.user_variables[UserVars.CORNERS_ONLY] = corners_only
            self.building_sides.append(BuildingSide(face, self.reference_cube, self, self.user_variables))







