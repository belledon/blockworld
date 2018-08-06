#!/bin/python3

import io
import os
import json
import pprint
import argparse
import collections
import numpy as np
from pyquaternion import Quaternion

from builders.simple_builder import SimpleBuilder
from towers.empty_tower import EmptyTower
from blocks.simple_block import SimpleBlock
from scenes.block_scene import BlockScene
from scenes.physics import TowerTester
from utils.json_encoders import TowerEncoder

materials = collections.OrderedDict(
    [('wood', 0.8),
     ('iron', 0.2)])

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
    base_dims = [3, 3]
    empty_tower = EmptyTower(base_dims)
    print('creating block for building')
    block_dims = [2, 1, 1]
    block = SimpleBlock(block_dims)

    max_blocks = args.number
    max_height = args.height
    builder = SimpleBuilder(max_blocks, max_height)

    new_tower = builder(empty_tower, block)

    tower_json = repr(new_tower)

    pprint.pprint(json.loads(tower_json))

    tester = TowerTester(json.loads(tower_json), materials)
    mat_tower, results = tester()

    pprint.pprint(results)

    pprint.pprint(mat_tower)
    scene = BlockScene(mat_tower)
    img_out = os.path.join(args.out, 'test_render')
    scene.render(img_out, [1], resolution = (512, 256))
    scene_out = os.path.join(args.out, 'test_scene.blend')
    scene.save(scene_out)
    # scene.render(img_out, [1], resolution = (1080, 720))
if __name__ == '__main__':
    main()
