import os
import sys
import bpy
import json
import argparse
import mathutils

import numpy as np
materials_path = os.path.dirname(os.path.realpath(__file__)) + '/materials.blend'
#################################################
# https://stackoverflow.com/questions/28075599/opening-blend-files-using-blenders-python-api
from bpy.app.handlers import persistent
@persistent
def load_handler(dummy):
    print("Load Handler:", bpy.data.filepath)
bpy.app.handlers.load_post.append(load_handler)
#################################################
def parser(args):

    p = argparse.ArgumentParser(description = 'Renders blockworld scene')
    p.add_argument('--scene', type = json.loads,
                   help = 'Tower json describing the scene.')
    p.add_argument('--trace', type = json.loads,
                   help = 'Trace json for physics.')
    p.add_argument('--out', type = str,
                   help = 'Path to save rendering')
    p.add_argument('--wireframe', action = 'store_true',
                   help = 'Render objects as wireframes')
    p.add_argument('--save_world', action = 'store_true',
                   help = 'Save the resulting blend scene')
    p.add_argument('--render_mode', type = str, default = 'default',
                   choices = ['default'],
                   help = 'mode to render')
    p.add_argument('--resolution', type = int, nargs = 2,
                   default = (256,256),  help = 'Render resolution')
    return p.parse_args(args)

class BlockScene:

    '''
    blendfile : The .blend world file
    scenefile : Either a .json file of parameters or a dictionary of the same
        structure
    frames : The total number of frames to render
    (optional) warmup : (default 6) The number of frames to bake prior to
        rendering. Sets the total number of bakes frames to `frames` + `warmup`
    '''

    def __init__(self, scene_json, trace = None, wire_frame = False):

        # Initialize attributes
        self.wire_frame = wire_frame
        self.trace = trace

        # Clear scene
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete(use_global=False)
        for item in bpy.data.meshes:
            bpy.data.meshes.remove(item)

        # Load materials and textures
        with Suppressor():
            bpy.ops.wm.open_mainfile(filepath=materials_path)

        if not trace is None:
            frames = len(trace['position'])
        else:
            frames = 1
        bpy.context.scene.frame_set(1)
        bpy.context.scene.frame_end = frames + 1
        # bpy.context.scene.frame_step = bp

        # Parse tower structure
        self.load_scene(scene_json)


    def select_obj(self, obj):
        """
        Brings the given object into active context.
        """
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.context.scene.objects.active
        bpy.context.scene.update()


    def rotate_obj(self, obj, rot):
        """
        Rotates the given object by the given quaternion.
        """
        self.select_obj(obj)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rot
        bpy.context.scene.update()

    def move_obj(self, obj, pos):
        """
        Moves the given object by the given 3-d vector.
        """
        self.select_obj(obj)
        pos = mathutils.Vector(pos)
        # print(obj.name, 'OLD POS', obj.location)
        # obj.data.transform(mathutils.Matrix.Translation(-pos))
        # obj.matrix_world.translation += pos
        obj.location = pos
        bpy.context.scene.update()
        print(obj.name, 'NEW POS', obj.location)

    def scale_obj(self, obj, dims):
        """
        Rescales to the object to the given dimensions.
        """
        self.select_obj(obj)
        obj.dimensions = dims
        bpy.context.scene.update()
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.context.scene.update()

    def set_appearance(self, obj, mat):
        """
        Assigns a material to a block.
        """
        if not mat in bpy.data.materials:
            raise ValueError('Unknown material {}'.format(mat))
        obj.active_material = bpy.data.materials[mat]
        bpy.context.scene.update()

    def create_block(self, object_d):
        """
        Initializes a block object.
        """
        bpy.ops.mesh.primitive_cube_add(location=object_d['data']['pos'],
                                        view_align=False,
                                        enter_editmode=False)
        ob = bpy.context.object
        ob.name = '{0:d}'.format(object_d['id'])
        ob.show_name = True
        me = ob.data
        me.name = '{0:d}_Mesh'.format(object_d['id'])
        self.scale_obj(ob, object_d['data']['dims'])
        ob.matrix_world.translation

        if 'appearance' in object_d['data'] and \
           'substance' in object_d['data']:
            mat = object_d['data']['appearance']
            mass = object_d['data']['substance']['density'] * \
                   np.prod(object_d['data']['dims'])
            friction = object_d['data']['substance']['friction']
        else:
            mat = 'Wood'
            phys_key = 'Wood'
            mass = substances.density[phys_key] * \
               np.prod(object_d['data']['dims'])
            friction = substances.friction[phys_key]

        self.set_appearance(ob, mat)
        if self.wire_frame:
            if ob.name == '5':
                self.set_appearance(ob, 'L')
            bpy.ops.object.mode_set(mode='EDIT')
            # bpy.ops.mesh.subdivide()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.modifier_add(type='WIREFRAME')
            ob.modifiers['Wireframe'].thickness = 0.2

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
        self.scale_obj(ob, (40, 40, 1))
        self.set_appearance(ob, 'Marble')
        if self.wire_frame:
            ob.cycles_visibility.diffuse = False
            ob.hide = True
            ob.hide_render = True

    def set_block(self, block):
        """
        Initializes blocks described in the block.
        """
        if block['id'] == 0:
            self.set_base(block['data'])
        else:
            self.create_block(block)

    def load_scene(self, scene_dict):
        # with open(scenefl, 'rU') as fl:
        if isinstance(scene_dict, str):
            scene_dict = json.loads(scene_dict)

        for block in scene_dict:
            self.set_block(block)

    def set_rendering_params(self, resolution):
        """
        Configures various settings for rendering such as resolution.
        """
        bpy.context.scene.render.fps = 60
        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.cycles.samples = 500
        bpy.context.scene.render.tile_x = 24
        bpy.context.scene.render.tile_y = 24
        bpy.context.scene.render.engine = 'CYCLES'

    def set_camera(self, rot):
        """
        Moves the camera along a circular path.
        Arguments:
            rot (float): angle in degrees along path (0, 360).
        """
        radius = 13.0
        theta = np.pi * (rot / 180.0)
        # Move camera to position on ring
        xyz = [np.cos(theta) * radius, np.sin(theta) * radius, 1]
        camera = bpy.data.objects['Camera']
        camera.location = xyz
        bpy.context.scene.update()
        # Face camera towards point
        loc_camera = camera.matrix_world.to_translation()
        direction = mathutils.Vector([0,0,3]) - loc_camera
        # point the cameras '-Z' and use its 'Y' as up
        rot_quat = direction.to_track_quat('-Z', 'Y')
        self.rotate_obj(camera, rot_quat)

    def frame_set(self, frame):
        bpy.context.scene.frame_set(frame)

        positions = np.array(self.trace['position'][frame])
        rotations = np.array(self.trace['rotation'][frame])
        n_blocks = positions.shape[0]
        for block_i in range(n_blocks):
            block = bpy.data.objects['{}'.format(block_i + 1)]
            self.move_obj(block, positions[block_i])
            self.rotate_obj(block, rotations[block_i])
            block.keyframe_insert(data_path='location', index = -1)
            block.keyframe_insert(data_path='rotation_quaternion', index = -1)

        bpy.context.scene.update()


    def render(self, output_name, frames, show = [],
               resolution = (256, 256), camera_rot = None):
        """
        output_name: Path to save frames
        frames: a list of frames to render (shifted by warmup)
        show: a list of object names to render
        """
        if not os.path.isdir(output_name):
            os.mkdir(output_name)
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
            out = os.path.join(output_name, '{0:d}'.format(i))
            self.set_camera(cam)
            bpy.context.scene.render.filepath = out
            self.frame_set(frame)
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
        self.set_rendering_params(resolution)
        n = int(dur * bpy.context.scene.render.fps)
        rots = np.linspace(0, 360, n)
        if freeze == True:
            frames = np.zeros(n).astype(int)
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
def main():
    argv = sys.argv
    print(argv[:6])
    if '--' in sys.argv:
        argv = sys.argv[sys.argv.index('--') + 1:]
    args = parser(argv)

    scene = BlockScene(args.scene, args.trace, wire_frame = args.wireframe)


    if args.render_mode == 'default':
        path = os.path.join(args.out, 'render')
        if not os.path.isdir(path):
            os.mkdir(path)

        frozen_path = os.path.join(path, 'frozen')
        scene.render_circle(frozen_path, freeze = True, dur = 2,
                            resolution = args.resolution)
        n_frames = len(args.trace['position'])
        motion_path = os.path.join(path, 'motion')
        scene.render(motion_path, np.arange(n_frames),
                     resolution = args.resolution)

    if args.save_world:
        path = os.path.join(args.out, 'world.blend')
        scene.save(path)

if __name__ == '__main__':
    main()
