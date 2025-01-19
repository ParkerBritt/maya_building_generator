import pymel.core as pm
import math
import random
from importlib import reload

import package.building.user_vars
reload(package.building.user_vars)
from package.building.user_vars import UserVars

class BuildingSide():
    def __init__(self, _face, reference_cube_transform, building, user_variables):
        self.mesh = building.reference_cube.getShape()
        self.user_variables = user_variables
        self.corners_only = user_variables[UserVars.CORNERS_ONLY]
        self.building = building
        self.ground_floor_height = self.user_variables[UserVars.GROUND_FLOOR_HEIGHT]
        self.top_padding = 50 
        self.group = self.building.group
        self.child_objects = []




        self.mesh_face = _face
        print("\n-------")
        print("face:", _face)

        self.normal = self.mesh_face.getNormal(space="world")

        # create matrix and sides
        self.face_m = pm.dt.Matrix() # identity matrix
        side = self.normal
        forward = self.normal.cross({0,-1,0})
        up = self.normal.cross(forward)

        # normalize vectors
        forward.normalize()
        side.normalize()
        up.normalize()

        # apply vectors to matrix
        self.face_m[0] = forward
        self.face_m[1] = up
        self.face_m[2] = side

        # get face bouding box
        face_pts = self.mesh_face.getPoints(space="world")
        face_min = [face_pts[0].x, face_pts[0].y, face_pts[0].z]
        face_max = [face_pts[0].x, face_pts[0].y, face_pts[0].z]
        for pt in face_pts:
            for j, comp in enumerate(pt):
                face_min[j] = min(face_min[j], comp)
                face_max[j] = max(face_max[j], comp)
        face_size = [math.sqrt(pow(face_max[0]-face_min[0],2)+pow(face_max[2]-face_min[2],2)), face_max[1]-face_min[1]]
        self.face_width = face_size[0]
        self.face_height = face_size[1]


        # instance geo
        # | window
        window_names = ["window_render_02", "window_render_03", "window_render_04"]
        self.window_geo = [pm.PyNode(window_name) for window_name in window_names]
        # | doors
        door_names = ["door_render_01", "door_render_02"]
        self.door_geo = [pm.PyNode(door_name) for door_name in door_names]
        # | trim
        self.floor_trim_geo = pm.PyNode("floor_trim")
        self.roof_trim_geo = pm.PyNode("roof_trim")
        self.bottom_bulkhead_geo = self.building.bottom_bulkhead_geo
        self.corner_piece = self.building.corner_piece[0]
        self.corner_decor_width = self.corner_piece.boundingBox().width()*self.user_variables[UserVars.HAS_CORNER_DECOR]



        window_height = self.window_geo[0].boundingBox().height();
        floor_density = self.user_variables[UserVars.FLOOR_DENSITY]
        self.uniform_padding = 0.05
        self.startv = (self.ground_floor_height+window_height/2)/self.face_height
        self.endv = (self.face_height-window_height-self.top_padding)/self.face_height

        self.upper_height = (self.endv-self.startv)*self.face_height

        # calculate floor count
        self.floor_cnt = self.upper_height/self.window_geo[0].boundingBox().height()+1
        self.floor_cnt = math.floor(self.floor_cnt)

        print("floor count before:", self.floor_cnt)

        # only apply density multiplier if it has enough floors
        if(round(self.floor_cnt * floor_density>3)):
            print("more than 3 floors, applying density and padding")
            self.floor_cnt *= floor_density

            # add padding to top and bottom
            self.uniform_padding /= floor_density
            self.startv += self.uniform_padding
            self.endv -= self.uniform_padding
            self.upper_height = (self.endv-self.startv)*self.face_height # recomputer upper_height
            
        self.floor_cnt = round(self.floor_cnt)
        print("floor count final:", self.floor_cnt)



        

        self.sort_face_points()


        self.all_boolean_objects = []
        self.door_boolean_objects = []
        # return

        # populate geometry
        if(self.user_variables[UserVars.HAS_CORNER_DECOR]):
            self.populate_corner_decor()

        self.populate_floor_trims()
        self.populate_roof_trims()

        if(self.corners_only):
            return

        self.populate_doors()
        self.populate_windows()
        self.bulkhead_geo = self.populate_bottom_bulkheads()

        self.bool_building(self.all_boolean_objects, True)
        # pm.parent(self.child_objects, self.group)

    def populate_bottom_bulkheads(self):
        instance_geo = self.bottom_bulkhead_geo
        y = 0

        sample = self.sampleMeshFace(0.5, y)

        transform = self.face_m.copy()
        transform[3] = sample
        transform[0]*=self.face_width/100

        # scale vertically
        vert_scale = self.user_variables[UserVars.BOTTOM_BULKHEAD_VERT_SCALE]
        if(vert_scale != 1):
            scale_m = pm.dt.Matrix()
            scale_m[1] = (0, vert_scale, 0, 0)
            transform = scale_m * transform


        bulkhead_copy = pm.general.duplicate(instance_geo)
        bulkhead_copy[0].set(transform)
        self.child_objects.append(bulkhead_copy)

        # scale uvs
        print("ATTEMPTING TO GET UVS FROM:", bulkhead_copy)
        print("SHAPE:", bulkhead_copy[0].getShape())
        uvs = bulkhead_copy[0].map[:]
        pm.select(uvs)
        pm.polyEditUV(scaleU=self.face_width/100, scaleV=vert_scale)

        if(len(self.door_boolean_objects) > 0):
            bool_result = pm.polyCBoolOp(bulkhead_copy[0].getShape(), *self.door_boolean_objects, op=2)

        return bulkhead_copy

        

    def sort_face_points(self):
        """Sort face points for consistant face sampling

        Uses the algorithm I wrote in my documentation
        """
        def sign(number):
            if(number<0):
                return -1
            elif(number>0):
                return 1
            else:
                return None

        face_pts = self.mesh_face.getPoints(space="world")
        normal_cross = self.normal.cross((0,1,0))
        compare_vector = pm.dt.Vector(1,0,-1)
        compare_vector.normalize()
        dot_product = self.normal.dot(compare_vector)

        # get mesh center
        self.mesh_center = pm.dt.Vector(0,0,0)
        for pt in face_pts:
            self.mesh_center += pm.dt.Vector(pt.x, pt.y, pt.z)
        self.mesh_center /= len(face_pts)

        self.face_pt1 = None
        self.face_pt2 = None
        self.face_pt3 = None
        self.face_pt4 = None

        for i, pt in enumerate(face_pts):
            center_to_pt_v = pt-self.mesh_center
            center_to_pt_v.normalize()
            x_sign = sign(normal_cross.dot(center_to_pt_v))
            y_sign = sign(pm.dt.Vector(0,1,0).dot(center_to_pt_v))
            if(x_sign==-1 and y_sign==-1):
                self.face_pt1 = pt
            elif(x_sign==1 and y_sign==-1):
                self.face_pt2 = pt
            elif(x_sign==-1 and y_sign==1):
                self.face_pt3 = pt
            elif(x_sign==1 and y_sign==1):
                self.face_pt4 = pt


    def bool_building(self, a_geo, is_set=False):
        """Perform boolean operation on geometry"""
        bool_result = None
        if(is_set):
            print("bool list:", *a_geo)
            if(len(a_geo)==0):
                return None
            bool_result = pm.polyCBoolOp(self.mesh, *a_geo, op=2)
        else:
            print("bool object:", a_geo)
            bool_result = pm.polyCBoolOp(self.mesh, a_geo, op=2)
        # bool_result = pm.polyCBoolOp(self.mesh, *a_geo, op=2)
        self.building.reference_cube = bool_result[0]
        self.building.reference_cube_shape = self.building.reference_cube.getShape()
        self.mesh = self.building.reference_cube.getShape()
        return bool_result

    def populate_floor_trims(self):
        """Place trims on ground floor"""
        instance_geo = self.floor_trim_geo
        upper_floors = self.floor_cnt-1
        for j in range(0,upper_floors):
            y = self.startv+(self.endv-self.startv) * (j)/max(upper_floors-1, 1)
            # center single floors
            if(upper_floors==1):
                y = self.startv+(self.endv-self.startv) * (0.5)

            sample = self.sampleMeshFace(0.5, y)

            transform = self.face_m.copy()
            transform[3] = sample
            transform[0]*=self.face_width/100

            # scale by floor_trim_height
            vert_scale = self.user_variables[UserVars.FLOOR_TRIM_HEIGHT]
            if(vert_scale!=1):
                scale_matrix = pm.dt.Matrix()
                scale_matrix[1]=[0,vert_scale,0,0]
                transform = scale_matrix*transform


            trim_copy = pm.general.duplicate(instance_geo)
            trim_copy[0].set(transform)
            self.child_objects.append(trim_copy)

            # scale uvs
            print("ATTEMPTING TO GET UVS FROM:", trim_copy)
            print("SHAPE:", trim_copy[0].getShape())
            uvs = trim_copy[0].map[:]
            pm.select(uvs)
            pm.polyEditUV(scaleU=self.face_width/100, scaleV=vert_scale)


    def populate_roof_trims(self):
        """Place trims on roof"""
        instance_geo = self.roof_trim_geo
        y = 1

        sample = self.sampleMeshFace(0.5, y)

        transform = self.face_m.copy()
        transform[3] = sample
        transform[0]*=self.face_width/100 + 0.5

        # scale vertically
        vert_scale = self.user_variables[UserVars.ROOF_TRIM_VERT_SCALE]
        if(vert_scale != 1):
            scale_m = pm.dt.Matrix()
            scale_m[1] = (0, vert_scale, 0, 0)
            transform = scale_m * transform

        trim_copy = pm.general.duplicate(instance_geo)
        # scale uvs
        print("ATTEMPTING TO GET UVS FROM:", trim_copy)
        print("SHAPE:", trim_copy[0].getShape())
        uvs = trim_copy[0].map[:]
        pm.select(uvs)
        pm.polyEditUV(scaleU=self.face_width/100+0.5, scaleV=vert_scale)

        trim_copy[0].set(transform)
        self.child_objects.append(trim_copy)




    def populate_corner_decor(self):
        """Place bricks on the building corners"""
        instance_geo = self.corner_piece
        instance_bbox = instance_geo.boundingBox()

        gap = 0.03
        decor_height = (instance_bbox.height()+gap)
        corner_decor_cnt = math.floor((self.face_height-decor_height)/decor_height)

        x = instance_bbox.width()/self.face_width/2
        for i in range(0, 2):
            sample = self.sampleMeshFace(x, 0)
            transform = self.face_m.copy()
            transform[3] = sample


            # flip for other side
            if(i==1):
                flip_m = pm.dt.Matrix()
                flip_m[0]=[-1,0,0,0]
                transform = flip_m * transform

            corner_piece_copy = pm.general.instance(instance_geo)
            corner_piece_copy[0].set(transform)
            x = 1-x

    def populate_doors(self):
        """Place doors on building"""
        instance_geo = self.door_geo[random.randint(0, len(self.door_geo)-1)]

        door_cnt = 10
        sample_x = 0

        door_width = instance_geo.boundingBox().width()
        # starting minimum sample
        min_door_sample = (self.corner_decor_width+door_width/2)/self.face_width

        for i in range(door_cnt):
            print("placing door:", i)

            # calculate door width
            door_width = instance_geo.boundingBox().width()

            # maximum random range to sample door position
            max_door_sample = 1-(self.corner_decor_width+door_width/2)/self.face_width

            # sample position on wall for door
            sample_x = random.uniform(min_door_sample, max_door_sample)

            print("min door sample:", min_door_sample)
            print("max door sample:", max_door_sample)
            print("sample x:", sample_x)
            if(sample_x>max_door_sample):
                print("door out of range, done placing doors")
                break
            sample = self.sampleMeshFace(sample_x, 0)

            # transform door onto wall
            transform = self.face_m.copy()
            transform[3] = sample
            door = pm.general.instance(instance_geo)
            door[0].set(transform)
            self.child_objects.append(door)
            # pm.parent(door, self.group)


            # create bounding box for boolean
            instance_geo_bounds = instance_geo.boundingBox()
            boolean_box = pm.polyCube(width=instance_geo_bounds.width()*0.5, height=instance_geo_bounds.height(), depth=instance_geo_bounds.depth())

            # transform boolean box on top of door
            bbox_center = instance_geo_bounds.center()
            door_boolean_m = pm.dt.Matrix()
            door_boolean_m[3] = [bbox_center.x, bbox_center.y, bbox_center.z, 1]
            door_boolean_m = door_boolean_m * transform
            boolean_box[0].set(door_boolean_m)

            # add to lists for later boolean
            self.all_boolean_objects.append(boolean_box)
            self.door_boolean_objects.append(boolean_box[0].duplicate())

            min_door_sample = sample_x+(door_width)/self.face_width
            instance_geo = self.door_geo[random.randint(0, len(self.door_geo)-1)]
            

    def populate_windows(self):
        """Place windows on building"""

        # geometry to use as window
        boolean_geo = pm.PyNode("window_01_boolean")


        # create start and end postions for for windows along face (normalized)
        # | get width (x) of window geo
        window_bbox = self.window_geo[0].boundingBox()
        window_width = window_bbox.width();
        window_height = window_bbox.height();
        # | offset start position by corner pieces
        side_gap = min(self.face_width*0.05, window_width*1)
        start_x = (self.corner_decor_width + window_width/2 + side_gap)/self.face_width
        start_x = min(start_x, 1)
        end_x = 1-start_x
        start_y = self.startv
        end_y = self.endv

        
        # determines how densely to distribute windows
        window_density = 0.95
        window_gap = min(self.face_width*abs(1-window_density), window_width*4)
        window_space_width = self.face_width-(self.corner_decor_width)*2-side_gap
        x_windows = math.floor(window_space_width/(window_width+window_gap))
        upper_floors = self.floor_cnt-1
        if(x_windows < 1 or upper_floors < 1):
            return



        # boolean_list = []
        for j in range(0,upper_floors):
            for i in range(0,x_windows):

                # creates a u position mapped between start_x and end_x
                # | fit_range * normalized value
                x = start_x+(end_x-start_x) * (i)/max(x_windows-1, 1)
                y = self.startv+(self.endv-self.startv) * (j)/max(upper_floors-1, 1)

                # center single floors
                if(upper_floors==1):
                    y = start_y+(end_y-start_y) * (0.5)

                sample = self.sampleMeshFace(x, y)

                transform = self.face_m.copy()
                transform[3] = sample
                transform_boolean = transform.copy()

                do_flip = bool(random.getrandbits(1))
                if(do_flip):
                    flip_m = pm.dt.Matrix()
                    flip_m[0]=[-1,0,0,0]
                    transform = flip_m * transform

                instance_geo = self.window_geo[random.randint(0, len(self.window_geo)-1)]
                window = pm.general.instance(instance_geo)
                window[0].set(transform)
                self.child_objects.append(window)

                # copy boolean geo
                boolean_geo_copy = pm.general.duplicate(boolean_geo)
                boolean_geo_copy[0].set(transform_boolean)

                self.all_boolean_objects.append(boolean_geo_copy)




    # samples to position at a certain planar coordinate using bilinear interpolation, only works on quads for now
    def sampleMeshFace(self, _u, _v):
        """Given parametric coordinates (u,v) returns 3D Position on face"""
        # sample_pos = self.sampleMeshFace_old(_u, _v)
        sample_pos =  self.sampleMeshFace_new(_u, _v)
        return sample_pos

    def sampleMeshFace_new(self, _u, _v):
        """Given parametric coordinates (u,v) returns 3D Position on face"""
        u = min(max(_u, 0), 1)
        v = min(max(_v, 0), 1)


        pt1 = self.face_pt1
        pt2 = self.face_pt2
        pt3 = self.face_pt4
        pt4 = self.face_pt3

        u_inv = 1-u
        v_inv = 1-v

        return (
                (pt1.x*u_inv + pt2.x*u)*v_inv + (pt4.x*u_inv + pt3.x*u)*v,
                (pt1.y*u_inv + pt2.y*u)*v_inv + (pt4.y*u_inv + pt3.y*u)*v,
                (pt1.z*u_inv + pt2.z*u)*v_inv + (pt4.z*u_inv + pt3.z*u)*v
               )

    def sampleMeshFace_old(self, _u, _v):
        """Given parametric coordinates (u,v) returns 3D Position on face"""
        u = min(max(_u, 0), 1)
        v = min(max(_v, 0), 1)

        face_pts = self.mesh_face.getPoints(space="world")

        # get face bouding box
        face_pts = self.mesh_face.getPoints(space="world")
        face_min = [face_pts[0].x, face_pts[0].y, face_pts[0].z]
        face_max = [face_pts[0].x, face_pts[0].y, face_pts[0].z]
        for pt in face_pts:
            for j, comp in enumerate(pt):
                face_min[j] = min(face_min[j], comp)
                face_max[j] = max(face_max[j], comp)

        pt1 = pm.dt.Point(face_min)
        pt2 = pm.dt.Point([face_max[0], face_min[1], face_max[2]])
        pt4 = pm.dt.Point([face_min[0], face_max[1], face_min[2]])
        pt3 = pm.dt.Point(face_max)

        u_inv = 1-u
        v_inv = 1-v

        return (
                (pt1.x*u_inv + pt2.x*u)*v_inv + (pt4.x*u_inv + pt3.x*u)*v,
                (pt1.y*u_inv + pt2.y*u)*v_inv + (pt4.y*u_inv + pt3.y*u)*v,
                (pt1.z*u_inv + pt2.z*u)*v_inv + (pt4.z*u_inv + pt3.z*u)*v
               )

