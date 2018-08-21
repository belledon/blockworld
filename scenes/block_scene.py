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

    def __init__(self, scene_json, frames = 1, warmup = 2, override={},
                 wire_frame = False):

        # Initialize attributes
        self.warmup = warmup
        self.frames = frames
        self.override = override
        self.wire_frame = wire_frame
        self.materials = ['Metal', 'Wood']
        self.density = [5.0, 1.0]
        self.friction = [0.2, 0.5]
        self.phys_objs = []

        # Clear scene
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete(use_global=False)
        for item in bpy.data.meshes:
            bpy.data.meshes.remove(item)

        # Load materials and textures
        with Suppressor():
            bpy.ops.wm.open_mainfile(filepath=materials_path)

        bpy.context.scene.frame_set(1)
        bpy.context.scene.frame_end = frames + warmup
        bpy.context.scene.frame_step = bpy.context.scene.frame_end - 1

        # Parse tower structure
        self.load_scene(scene_json)


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

    def set_appearance(self, b_id, mat):
        """
        Assigns a material to a block.
        """
        obj = bpy.data.objects[b_id]
        obj.active_material = bpy.data.materials[mat]
        bpy.context.scene.update()

    def create_block(self, object_d):
        """
        Initializes a block object.
        """
        block = object_d['block']
        bpy.ops.mesh.primitive_cube_add(location=block['pos'],
                                        view_align=False,
                                        enter_editmode=False)
        ob = bpy.context.object
        ob.name = '{0:d}'.format(object_d['id'])
        ob.show_name = True
        me = ob.data
        me.name = '{0:d}_Mesh'.format(object_d['id'])
        self.scale_obj(ob, block['dims'])
        ob.matrix_world.translation

        if 'material' in object_d and 'congruency' in object_d:
            cong = int(object_d['congruency'])
            mat = self.materials[object_d['material']]
            phys_key = not (cong ^ object_d['material'])
            mass = self.density[phys_key] * \
                   np.prod(block['dims'])
            friction = self.friction[phys_key]
        else:
            mat = 'Wood'
            mass = self.density[1] * np.prod(block['dims'])
            friction = self.friction[1]

        ob.active_material = bpy.data.materials[mat]
        bpy.ops.rigidbody.objects_add(type='ACTIVE')
        ob.rigid_body.use_margin = 1
        ob.rigid_body.collision_margin = 0.0
        ob.rigid_body.mass = mass
        ob.rigid_body.friction = friction
        phys_objs = self.phys_objs
        phys_objs.append(object_d['id'])
        self.phys_objs = phys_objs

    def set_base(self, block):
        """
        Creates the table on which the blocks will stand.
        """
        bpy.ops.mesh.primitive_cylinder_add(
            location = block['pos'],
            view_align=False,
            enter_editmode=False)
        ob = bpy.context.object
        ob.name = 'base'
        ob.show_name = False
        ob.data.name = '{}_Mesh'.format('base')
        self.scale_obj(ob, (10, 10, 1))
        self.set_appearance('base', 'Marble')
        bpy.ops.rigidbody.object_add(type='PASSIVE')
        bpy.ops.rigidbody.constraint_add(type='FIXED')
        # Set to deal with issues like jittering
        ob.rigid_body.use_margin = 1
        ob.rigid_body.collision_margin = 0.0

    def set_block(self, stack):
        """
        Initializes blocks described in the stack.
        """
        if stack['id'] == 0:
            self.set_base(stack['block'])
        else:
            self.create_block(stack)

    def load_scene(self, scene_dict):
        # with open(scenefl, 'rU') as fl:
        if isinstance(scene_dict, str):
            scene_dict = json.loads(scene_dict)

        if not scene_dict['directed']:
            raise ValueError('Improperly formated json')

        # self.set_base(scene_dict['block']['dims'], scene_dict['position'])

        for block in scene_dict['nodes']:
            self.set_block(block)

    def set_rendering_params(self, resolution):
        """
        Configures various settings for rendering such as resolution.
        """
        bpy.context.scene.render.fps = 60
        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.cycles.samples = 1000
        bpy.context.scene.render.tile_x = 16
        bpy.context.scene.render.tile_y = 16
        bpy.context.scene.render.engine = 'CYCLES'

    def set_camera(self, rot):
        """
        Moves the camera along a circular path.

        Arguments:
            rot (float): angle in degrees along path (0, 360).
        """
        radius = 6.0
        theta = rot / (2 * np.pi)
        # Move camera to position on ring
        xyz = [np.cos(theta) * radius, np.sin(theta) * radius, radius]
        camera = bpy.data.objects['Camera']
        camera.location = xyz
        # Face camera towards point
        loc_camera = camera.matrix_world.to_translation()
        direction = mathutils.Vector([0,0,1]) - loc_camera
        # point the cameras '-Z' and use its 'Y' as up
        rot_quat = direction.to_track_quat('-Z', 'Y')
        self.rotate_obj(camera, rot_quat)


    def bake_physics(self):
        bpy.context.scene.rigidbody_world.point_cache.frame_end = bpy.context.scene.frame_end
        bpy.context.scene.rigidbody_world.solver_iterations = 100
        bpy.context.scene.rigidbody_world.steps_per_second = 240
        bpy.context.scene.rigidbody_world.time_scale = 1
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

    def get_trace(self, frames = None):
        """
        Obtains world state for select frames.
        Currently returns the position of each rigid body.
        """
        if frames is None:
            frames = range(bpy.context.scene.frame_end - self.warmup)

        n_objs = len(self.phys_objs)
        results = []
        for frame in frames:
            bpy.context.scene.frame_set(frame + self.warmup)
            bpy.context.scene.update()

            frame_d = {}
            positions = np.zeros((n_objs, 3))
            for obj_id in self.phys_objs:
                obj_ind = int(obj_id) - 1
                ob = bpy.context.scene.objects[obj_id]
                positions[obj_ind] = ob.matrix_world.to_translation()

            frame_d['position'] = positions
            results.append(frame_d)

        return results

    def render(self, output_name, frames, show = [],
               resolution = (256, 256), camera_rot = None):
        """
        output_name: Path to save frames
        frames: a list of frames to render (shifted by warmup)
        show: a list of object names to render
        """
        self.set_rendering_params(resolution)
        if len(show) > 0:

            for obj in bpy.context.scene.objects:
                if not obj.name in show:
                    # print("Hiding {0!s}".format(o_name))
                    obj.cycles_visibility.diffuse = False
                    obj.hide = True
                    obj.hide_render = True

        if camera_rot is None:
            camera_rot = np.zeros(len(frames))

        for i, (frame, cam) in enumerate(zip(frames, camera_rot)):
            out = "{!s}_{:d}".format(output_name, i)
            self.set_camera(cam)
            bpy.context.scene.render.filepath = out
            bpy.context.scene.frame_set(frame + self.warmup)
            bpy.context.scene.update()
            bpy.ops.render.render(write_still=True)


    def render_circle(self, out_path, freeze = True, dur = 1,
                      resolution = (256, 256)):
        """
        Renders a ring around a tower.

        Arguments:
            out_path (str): Path to save frames.
            freeze (bool): Whether or not to run physics.
            dur (float, optional): Duration in seconds.
            resolution (float, optional): Resolution of render.
        """
        # n = dur * bpy.context.scene.render.fps
        n = 10
        rots = np.linspace(0, 360, n)
        if freeze == True:
            frames = np.repeat(0, n)
        else:
            frames = np.arange(n)

        self.render(out_path, frames, resolution = resolution,
                    camera_rot = rots)


    def save(self, out):
        """
        Writes the scene as a blend file.
        """
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
