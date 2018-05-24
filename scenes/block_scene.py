import os
import sys
import bpy
import json
import traceback
import mathutils
import numpy as np
from math import *
from abc import ABC, abstractmethod


#################################################
# https://stackoverflow.com/questions/28075599/opening-blend-files-using-blenders-python-api
from bpy.app.handlers import persistent
@persistent
def load_handler(dummy):
    print("Load Handler:", bpy.data.filepath)
bpy.app.handlers.load_post.append(load_handler)
#################################################

'''
    blendfile : The .blend world file
    scenefile : Either a .json file of parameters or a dictionary of the same
        structure
    frames : The total number of frames to render
    (optional) warmup : (default 6) The number of frames to bake prior to
        rendering. Sets the total number of bakes frames to `frames` + `warmup`
'''


class BlockScene:

    def __init__(self, scene_json, frames, warmup = 3, override={},
                 wire_frame = False):

        self.warmup = warmup
        self.frames = frames
        self.override = override
        self.wire_frame = wire_frame
        self.phys_objs = []
        # with Suppressor():
        #     bpy.ops.wm.open_mainfile(filepath=blendfile)
        self.load_scene(scenefile)
        bpy.context.scene.frame_set(1)
        bpy.context.scene.frame_end = frames + warmup
        bpy.context.scene.frame_step = bpy.context.scene.frame_end - 1

    def select_obj(self, obj):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.context.scene.objects.active
        bpy.context.scene.update()

    def set_smoothness(self, obj, smooth = True):
        for poly in obj.data.polygons:
            poly.use_smooth = smooth

    def copy_obj(self, objname,newname='None'):

        source = bpy.data.objects[objname]
        # mat = source.data.materials[0]
        new_obj = source.copy()
        new_obj.data = source.data.copy()
        new_obj.name = newname
        new_obj.animation_data_clear()

        self.move_obj(new_obj, (0,0,-10)) # Temporarily place under the ground

        bpy.context.scene.objects.link(new_obj)
        bpy.context.scene.rigidbody_world.group.objects.link(new_obj)

        new_obj.rigid_body.mass = source.rigid_body.mass
        new_obj.rigid_body.friction = source.rigid_body.friction
        new_obj.rigid_body.use_margin = True
        new_obj.rigid_body.collision_margin = source.rigid_body.collision_margin
        new_obj.rigid_body.collision_shape = source.rigid_body.collision_shape
        # To ensure that density plays more of a roll
        # new_obj.rigid_body.restitution = source.rigid_body.restitution
        new_obj.rigid_body.restitution = 0.5

        return new_obj

    def resize_obj(self, objname, dims):
        obj = bpy.data.objects[objname]
        scales = dims / np.asarray(obj.dimensions)
        obj.scale[0] *= scales[0]
        obj.scale[1] *= scales[1]
        obj.scale[2] *= scales[2]
        bpy.context.scene.update()


    def move_obj(self, obj, pos):
        obj.location = pos
        bpy.context.scene.update()


    def init_lighting(self, strength = 1., color = (1.,1.,1.)):
        scene = bpy.context.scene
        # Create new lamp datablock
        lamp_data = bpy.data.lamps.new(name="New Lamp", type='POINT')
        lamp_data.node_tree.nodes['Emission'].inputs['Strength'].default_value = 10
        # Create new object with our lamp datablock
        lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
        # Link lamp object to the scene so it'll appear in this scene
        scene.objects.link(lamp_object)
        # Place lamp to a specified location
        lamp_object.location = (0.0, 0.0, 9.0)


    def set_rendering_params(self, resolution = (256, 256)):
        bpy.context.scene.render.fps = 60

        if 'resolution' in self.override:
            resolution = self.override['resolution']
        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.cycles.samples = 1000
        # bpy.context.user_preferences.addons['cycles'].preferences.compute_device_type = "CUDA"
        bpy.context.scene.render.tile_x = 16
        bpy.context.scene.render.tile_y = 16

    def set_smoothness(self, obj, smooth = True):
        for poly in obj.data.polygons:
            poly.use_smooth = smooth


    def creat_block(self, b_id, dimensions, pos, rot):
        """
        Initializes a block object.
        """
        bpy.ops.mesh.primitive_cone_add(
            view_align=False,
            enter_editmode=False,
            location=pos,
            rotation=list(rot))
        ob = bpy.context.object
        ob.name = b_id
        ob.show_name = True
        me = ob.data
        me.name = name+'Mesh'
        self.resize_obj(b_id, dimensions)


    def set_block(self, stack):
        """
        Initializes blocks described in the stack.

        Recursively initializes children.
        """
        self.create_block(stack['id'], stack['block']['dims'],
                                stack['position'], stack['orientation'])

        if 'children' in stack:
            children = stack['children']
            for child in children:
                self.set_block(child)

    def set_base(self, dimensions, pos):
        self.create_block('base', dimensions, position, [1, 0, 0, 0])

    def load_scene(self, scenefl):
        with open(scenefl, 'rU') as fl:
            scene_dict = json.loads(fl.read())

        if 'base' not in scene_dict:
            raise ValueError('Improperly formated json')

        self.set_base(scene_dict['block']['dims'], scene_dict['position'])

        for stack in scene_dict['children']:
            self.set_block(stack)


    def bake_physics(self):

        bpy.context.scene.rigidbody_world.point_cache.frame_end = bpy.context.scene.frame_end
        bpy.context.scene.rigidbody_world.solver_iterations = 100
        bpy.context.scene.rigidbody_world.steps_per_second = 240 # CHANGE BACK TO 240 AFTER DEBUGGING!!!!!
        bpy.context.scene.rigidbody_world.time_scale = 10
        bpy.context.scene.rigidbody_world.use_split_impulse = 1

        # https://blender.stackexchange.com/questions/35621/setting-overriding-context-for-rigid-body-bake
        bpy.context.scene.update()
        for p_obj in self.phys_objs:
            object = bpy.context.scene.objects[p_obj]
            override = {'scene': bpy.context.scene,
                        'point_cache': bpy.context.scene.rigidbody_world.point_cache,
                        'active_object':object
                        }
            # bake to current frame
            with Suppressor():
                bpy.ops.ptcache.bake(override, bake=True)
            break

    def get_position(self, obj_name):
        obj = bpy.context.scene.objects[obj_name]
        pos = obj.matrix_world.to_translation()
        return np.around(pos, decimals = 3)

    def get_rotation(self, obj_name):
        obj = bpy.context.scene.objects[obj_name]
        _, r, _ = obj.matrix_world.decompose()
        return np.array(r.to_euler())  * (180 / np.pi)

    def get_positions(self, objs, frame):
        '''
        objs : A list of object names
        frame : The frame to retrieve positions. This is adjusted by the
            warmup
        '''
        positions = np.zeros((len(objs), 3))
        return self.get_observation(objs, frame, self.get_position, positions)


    def get_rotations(self, objs, frame):
        '''
        objs : A list of object names
        frame : The frame to retrieve positions. This is adjusted by the
            warmup
        '''
        rotations = np.zeros((len(objs), 3))
        return self.get_observation(objs, frame, self.get_rotation, rotations)


    def get_observation(self, objs, frame, func, out):
        for i,o in enumerate(objs):

            bpy.context.scene.frame_set(frame + self.warmup)
            bpy.context.scene.update()
            out[i] = func(o)
        return out

    def get_coords(self, obj):
        return np.array([(obj.matrix_world * v.co) for v in obj.data.vertices])

    # '''
    # Uses ray casting to determing if to objects have collided
    # '''
    # def colliding(self, src, target):
    #     a = bpy.context.scene.objects[target]
    #     b = bpy.context.scene.objects[src]
    #     self.select_obj(b)

    #     mw = b.matrix_world
    #     mwi = mw.inverted()

    #     # src and dst in local space of cb
    #     origin = mwi * a.matrix_world.to_translation()
    #     dest = mwi * b.matrix_world.to_translation()

    #     direction = np.array((dest - origin).normalized())
    #     thresh = np.linalg.norm( a.dimensions * 0.5)

    #     hit, loc, _, face = b.ray_cast(origin, direction, thresh)
    #     # print(bpy.context.scene.frame_current, 'p', (dest, origin), 'd', direction, 't', thresh, 'h', hit)
    #     return hit

    # def get_velocity(self, obj_name, frame):
    #     assert(frame >= 1)
    #     # t-1
    #     bpy.context.scene.frame_set(frame-1)
    #     p0 = self.get_position(obj_name)
    #     #t
    #     bpy.context.scene.frame_set(frame)
    #     p1 = self.get_position(obj_name)
    #     # dp / dt
    #     dt = np.around(1 / bpy.context.scene.render.fps, decimals = 3)
    #     delta = (p1-p0) / dt
    #     return delta

    """
        output_name: Path to save frames
        frames: a list of frames to render (shifted by warmup)
        show: a list of object names to render
    """
    def render(self, output_name, frames, show = []):

        if len(show) > 0:

            for obj in bpy.context.scene.objects:
                if not obj.name in show:
                    # print("Hiding {0!s}".format(o_name))
                    obj.cycles_visibility.diffuse = False
                    obj.hide = True
                    obj.hide_render = True

        for frame in frames:

            out = "{!s}_{:d}".format(output_name, frame)
            bpy.context.scene.render.filepath = out
            bpy.context.scene.frame_set(frame + self.warmup)
            bpy.context.scene.update()
            bpy.ops.render.render(write_still=True)


# From https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions
class Suppressor(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).
    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds =  [os.open(os.devnull,os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0],1)
        os.dup2(self.null_fds[1],2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0],1)
        os.dup2(self.save_fds[1],2)
        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)
