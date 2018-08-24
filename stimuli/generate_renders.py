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
import argparse
import numpy as np

from scenes.generator import Generator
from scenes import block_scene

def simulate_tower(tower, path):
    """
    Helper function that processes a tower.
    """

    with open(tower, 'r') as f:
        tower_json = json.load(f)

    tower_full = os.path.join(path, 'full')
    tower_wire = os.path.join(path, 'wire')
    # if not os.path.isdir(tower_full):
    #     os.mkdir(tower_full)
    # if not os.path.isdir(tower_wire):
    #     os.mkdir(tower_wire)

    scene = block_scene.BlockScene(tower_json, wire_frame = False, frames = 120)
    scene.bake_physics()
    scene.render(tower_full, np.arange(120, step= 10), resolution = (512, 512),
                 camera_rot = np.repeat(100, 120))
    del scene

    scene = block_scene.BlockScene(tower_json, wire_frame = True, frames = 120)
    scene.bake_physics()
    scene.render(tower_wire, np.arange(120, step= 10), resolution = (512, 512),
                 camera_rot = np.repeat(100, 120))


def main():
    parser = argparse.ArgumentParser(
        description = 'Renders the towers in a given directory')
    parser.add_argument('src', type = str, help = 'Path to tower jsons')
    parser.add_argument('out', type = str, help = 'Path to save renders.')

    args = parser.parse_args()

    if not os.path.isdir(args.out):
        os.mkdir(args.out)
    tower_j = args.src
    tower_name = os.path.splitext(os.path.basename(tower_j))[0]
    tower_base = os.path.join(args.out, tower_name)
    if not os.path.isdir(tower_base):
        os.mkdir(tower_base)
    simulate_tower(tower_j, tower_base)

if __name__ == '__main__':
    main()
