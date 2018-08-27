#!/bin/python3
""" Generates mutations for given towers.
"""

import os
import glob
import json
import pprint
import argparse
import numpy as np

import towers
from scenes.generator import Generator
from scenes import block_scene

def simulate_tower(tower, path):
    """
    Helper function that processes a tower.
    """
    tower_json = tower.serialize()
    scene = block_scene.BlockScene(tower_json, wire_frame = False, frames = 120)
    blend_path = '{0!s}.blend'.format(path)
    scene.bake_physics()
    scene.save(blend_path)


def main():
    parser = argparse.ArgumentParser(
        description = 'Generates mutations on given towers')
    parser.add_argument('src', type = str, help = 'Path to tower jsons')
    parser.add_argument('out', type = str, help = 'Path to save mutations.')
    args = parser.parse_args()

    if not os.path.isdir(args.out):
        os.mkdir(args.out)

    materials = {'Wood' : 1.0}
    gen = Generator(materials, 'local')

    for tower_j in glob.glob(os.path.join(args.src, '*.json')):
        base = towers.simple_tower.load(tower_j)
        tower_name = os.path.splitext(os.path.basename(tower_j))[0]
        tower_path = os.path.join(args.out, tower_name)
        alternates = gen.configurations(base)

        for b_id,b  in enumerate(alternates):
            b_path = '{0!s}_b_{1:d}'.format(tower_path, b_id)
            for mat in b:
                m_path = '{0!s}_m_{1!s}_con.json'.format(b_path, mat)
                con, inc = b[mat]
                with open(m_path, 'w') as f:
                    json.dump(con.serialize(), f, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
