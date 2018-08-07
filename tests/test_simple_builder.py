#!/bin/python3

import io
import os
import json
import pprint
import argparse
import numpy as np
from pyquaternion import Quaternion

from builders.simple_builder import SimpleBuilder
from towers.empty_tower import EmptyTower
from blocks.simple_block import SimpleBlock
from scenes.block_scene import BlockScene
from utils.json_encoders import TowerEncoder

# rotations = [Quaternion(axis=[1, 0, 0], angle = np.pi/2),
#              Quaternion(axis=[0, 1, 0], angle = np.pi/2),
#              Quaternion(axis=[0, 0, 1], angle = np.pi/2),
#              Quaternion(axis=[1, 0, 0], angle = 0)]

rotations = [Quaternion(axis=[1, 0, 0], angle = 0),]
             # Quaternion(axis=[0, 1, 0], angle = np.pi/2)]

def main():
    parser = argparse.ArgumentParser(description = ('Tests `SimpleBuilder` '+\
                                                   'and associated classes'))

    parser.add_argument('out', type = str, help = 'Path to save render.')
    parser.add_argument('--number', type = int, default = 2,
                        help = 'Number of blocks.')
    parser.add_argument('--height', type = float, default = 10,
                        help = 'Height of the tower.')

    args = parser.parse_args()

    print('creating starting tower')
    base_dims = [2, 2]
    empty_tower = EmptyTower(base_dims)
    print('creating block for building')
    block_dims = [2, 1, 1]
    block = SimpleBlock(block_dims)

    max_blocks = args.number
    max_height = args.height
    builder = SimpleBuilder(max_blocks, max_height)

    new_tower = builder(empty_tower, block)

    tower_json = repr(new_tower)

    pprint.pprint(json.loads(repr(new_tower)))
    with open(os.path.join(args.out, 'test.json'), 'w') as f:
        json.dump(json.loads(tower_json), f, indent = 4, sort_keys = True)

    scene = BlockScene(tower_json)
    img_out = os.path.join(args.out, 'test_render')
    scene.render(img_out, [1])
    scene_out = os.path.join(args.out, 'test_scene.blend')
    scene.save(scene_out)

if __name__ == '__main__':
    main()
