#!/bin/python3
""" Generates renderings of towers for academic figures.

For a given tower, two sets of images will be generated:

1) With textures and background
2) With wireframe and no background
"""

import os
import glob
import json
import pprint
import json
import shlex
import argparse
import subprocess
import numpy as np
from dask import distributed

# from config import Config
from blockworld import towers, blocks
from blockworld.simulation import tower_scene
from blockworld.utils import json_encoders


# CONFIG = Config()

render_path = 'blockworld/simulation/render.py'
mat_path = 'blockworld/simulation/materials.blend'
cmd = '/blender/blender --background -P {0!s}'

def render(scene, trace, out):
    scene_s = json.dumps(scene)
    trace_s = json.dumps(trace, cls = json_encoders.TowerEncoder)
    _cmd = cmd.format(render_path)
    _cmd = shlex.split(_cmd)
    _cmd += [
        '--',
        '--out',
        out,
        '--save_world',
        '--scene',
        scene_s,
        '--trace',
        trace_s,
        '--render_mode',
        'none'
    ]
    # _cmd = shlex.split(cmd.format(render_path, scene_s, trace_s, out))
    # _cmd = ['/blender/blender',
    #         '--background ',
    #         '--python {}'.format(render_path),
    #         '--scene {}'.format(scene_s),
    #         '--trace {}'.format(trace_s),
    #         '--out {}'.format(out)]
    # print(' '.join(_cmd[:-3]))
    subprocess.run(_cmd)

def simulate_tower(tower_j):
    """
    Helper function that processes a tower.
    """
    tower = towers.simple_tower.load(tower_j)
    tower_s = tower.serialize()
    keys = list(tower.blocks.keys())[1:]
    with tower_scene.TowerPhysics(tower_s) as scene:
        trace = scene.get_trace(120, keys)
    return trace


def main():
    parser = argparse.ArgumentParser(
        description = 'Renders the towers in a given directory')
    parser.add_argument('--src', type = str, default = 'data/towers',
                        help = 'Path to tower jsons')

    args = parser.parse_args()

    # src = os.path.join(CONFIG['data'], args.src)
    src = args.src
    out = args.src + '_render'
    # if not os.path.isdir(out):
    #     os.mkdir(out)

    cluster = distributed.LocalCluster( n_workers = 4, threads_per_worker = 1)
    print(cluster.dashboard_link)
    client = distributed.Client(cluster)

    tower_jsons = glob.glob(os.path.join(src, '*.json'))
    futures = client.map(simulate_tower, tower_jsons)
    results = client.gather(futures)
    print(results[0])
if __name__ == '__main__':
    main()
