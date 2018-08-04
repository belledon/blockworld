import os
import sys
import bpy
import json
import pprint
import traceback
import mathutils
import numpy as np
import mathutils


#################################################
# https://stackoverflow.com/questions/28075599/opening-blend-files-using-blenders-python-api
from bpy.app.handlers import persistent
@persistent
def load_handler(dummy):
    print("Load Handler:", bpy.data.filepath)
bpy.app.handlers.load_post.append(load_handler)
#################################################



materials_path = os.path.dirname(os.path.realpath(__file__)) + '/materials.blend'


class BlockScene:

    '''
    blendfile : The .blend world file
    scenefile : Either a .json file of parameters or a dictionary of the same
        structure
    frames : The total number of frames to render
    (optional) warmup : (default 6) The number of frames to bake prior to
        rendering. Sets the total number of bakes frames to `frames` + `warmup`
    '''

    def __init__(self, scene_json, frames = 1, warmup = 3, override={},
                 wire_frame = False):

        self.warmup = warmup
        self.frames = frames
        self.override = override
        self.wire_frame = wire_frame
        self.phys_objs = []
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete(use_global=False)
        for item in bpy.data.meshes:
            bpy.data.meshes.remove(item)
        with Suppressor():
            bpy.ops.wm.open_mainfile(filepath=materials_path)

        self.load_scene(scene_json)
        bpy.context.scene.frame_set(1)
        bpy.context.scene.frame_end = frames + warmup
        bpy.context.scene.frame_step = bpy.context.scene.frame_end - 1


    def select_obj(self, obj):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.context.scene.objects.active
        bpy.context.scene.update()


    def rotate_obj(self, obj, rot):
        self.select_obj(obj)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rot
        bpy.context.scene.update()

    def move_obj(self, obj, pos):
        self.select_obj(obj)
        pos = mathutils.Vector(pos)
        print(obj.name, 'OLD POS', obj.location)
        obj.data.transform(mathutils.Matrix.Translation(-pos))
        obj.matrix_world.translation += pos
        # obj.location = pos
        bpy.context.scene.update()
        print(obj.name, 'NEW POS', obj.location)

    def scale_obj(self, obj, dims):
        self.select_obj(obj)
        obj.dimensions = dims
        bpy.context.scene.update()
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.context.scene.update()


    def create_block(self, b_id, dimensions, pos):
        """
        Initializes a block object.
        """
        bpy.ops.mesh.primitive_cube_add(location=pos,
                                        view_align=False,
                                        enter_editmode=False)
        ob = bpy.context.object
        ob.name = b_id
        ob.show_name = True
        me = ob.data
        me.name = '{}_Mesh'.format(b_id)
        # self.move_obj(ob, pos)
        self.scale_obj(ob, dimensions)
        # self.rotate_obj(ob, rot)
        ob.matrix_world.translation

    def set_appearance(self, b_id, mat):
        obj = bpy.data.objects[b_id]
        obj.active_material = bpy.data.materials[mat]
        bpy.context.scene.update()


    def set_block(self, stack):
        """
        Initializes blocks described in the stack.
        """
        if stack['id'] == 'base':
            self.set_base(stack['block']['dims'], stack['position'])
            self.set_appearance('base', 'Plastic')
        else:
            self.create_block(stack['id'], stack['block']['dims'],
                                stack['position'])
            if 'appearance' in stack:
                self.set_appearance(stack['id'], stack['appearance'])
            else:
                self.set_appearance(stack['id'], 'Wood')

    def set_base(self, dimensions, pos):
        bpy.ops.mesh.primitive_cylinder_add(
            location=pos,
            view_align=False,
            enter_editmode=False)
        ob = bpy.context.object
        ob.name = 'base'
        ob.show_name = False
        me = ob.data
        me.name = '{}_Mesh'.format('base')
        self.scale_obj(ob, (10, 10, 1))
        ob.matrix_world.translation


    def load_scene(self, scene_dict):
        # with open(scenefl, 'rU') as fl:
        scene_dict = json.loads(scene_dict)

        print('Loading scene:')

        if not scene_dict['directed']:
            raise ValueError('Improperly formated json')

        # self.set_base(scene_dict['block']['dims'], scene_dict['position'])

        for block in scene_dict['nodes']:
            self.set_block(block)

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
        bpy.context.scene.render.tile_x = 16
        bpy.context.scene.render.tile_y = 16
        bpy.context.scene.render.engine = 'CYCLES'

    def bake_physics(self):

        bpy.context.scene.rigidbody_world.point_cache.frame_end = bpy.context.scene.frame_end
        bpy.context.scene.rigidbody_world.solver_iterations = 100
        bpy.context.scene.rigidbody_world.steps_per_second = 240
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

    """
        output_name: Path to save frames
        frames: a list of frames to render (shifted by warmup)
        show: a list of object names to render
    """
    def render(self, output_name, frames, show = []):
        print('rendering')
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

    def save(self, out):
        bpy.ops.wm.save_as_mainfile(filepath=out)

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
