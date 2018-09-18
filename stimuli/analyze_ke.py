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

from config import Config
import towers
from simulation import physics

CONFIG = Config()

def simulate_tower(tower, path):
    """
    Helper function that processes a tower.
    """
    p = physics.TowerEntropy()
    t = towers.simple_tower.load(tower)
    return p(t)


def main():
    parser = argparse.ArgumentParser(
        description = 'Renders the towers in a given directory')
    parser.add_argument('--src', type = str, default = 'towers',
                        help = 'Path to tower jsons')

    args = parser.parse_args()

    src = os.path.join(CONFIG['data'], args.src)
    out = ''
    # out = os.path.join(CONFIG['data'], '{0!s}_rendered'.format(args.src))

    # if not os.path.isdir(out):
    #     os.mkdir(out)

    for tower_j in glob.glob(os.path.join(src, '*.json')):
        tower_name = os.path.splitext(os.path.basename(tower_j))[0]
        tower_base = os.path.join(out, tower_name)
        # if not os.path.isdir(tower_base):
        #     os.mkdir(tower_base)
        print('tower: {}'.format(tower_base))
        ke = simulate_tower(tower_j, tower_base)
        pprint.pprint(ke)

if __name__ == '__main__':
    main()
