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

# from config import Config
from blockworld import towers, blocks
from blockworld.simulation import physics

# CONFIG = Config()

def simulate_tower(tower):
    """
    Helper function that processes a tower.
    """
    p = physics.TowerEntropy()
    t = towers.simple_tower.load(tower)
    return p(t)


def main():
    parser = argparse.ArgumentParser(
        description = 'Renders the towers in a given directory')
    parser.add_argument('--src', type = str, default = '../data/towers',
                        help = 'Path to tower jsons')

    args = parser.parse_args()

    # src = os.path.join(CONFIG['data'], args.src)
    src = args.src
    out = ''
    for tower_j in glob.glob(os.path.join(src, '*.json')):
        tower_name = os.path.splitext(os.path.basename(tower_j))[0]
        tower_base = os.path.join(out, tower_name)
        print('tower: {}'.format(tower_base))
        ke = simulate_tower(tower_j)
        pprint.pprint(ke[0])

if __name__ == '__main__':
    main()
