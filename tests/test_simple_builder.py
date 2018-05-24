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


# rotations = [Quaternion(axis=[1, 0, 0], angle = np.pi/2),
#              Quaternion(axis=[0, 1, 0], angle = np.pi/2),
#              Quaternion(axis=[0, 0, 1], angle = np.pi/2),
#              Quaternion(axis=[1, 0, 0], angle = 0)]

rotations = [Quaternion(axis=[1, 0, 0], angle = 0)]

def main():
    parser = argparse.ArgumentParser(description = ('Tests `SimpleBuilder` '+\
                                                   'and associated classes'))

    parser.add_argument('out', type = str, help = 'Path to save render.')

    # args = parser.parse_args()
    print('creating starting tower')
    base_dims = [4, 4]
    empty_tower = EmptyTower(base_dims)
    print('creating block for building')
    block_dims = [3, 2, 1]
    block = SimpleBlock(block_dims)

    max_blocks = 3
    max_height = 100
    builder = SimpleBuilder(max_blocks, max_height)

    new_tower = builder(empty_tower, block, rotations)

    tower_json = new_tower.serialize()

    pprint.pprint(tower_json)

    json_io = io.BytesIO(json.dumps(tower_json))

    scene = BlockScene(json_io)
    img_out = os.path.join(args.out, 'test_render')
    scene.render(img_out, 1)


if __name__ == '__main__':
    main()
