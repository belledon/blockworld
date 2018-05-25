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

rotations = [Quaternion(axis=[1, 0, 0], angle = np.pi/2),
             Quaternion(axis=[0, 1, 0], angle = np.pi/2),
             Quaternion(axis=[0, 0, 1], angle = np.pi/2),
             Quaternion(axis=[1, 0, 0], angle = 0)]

rotations = [Quaternion(axis=[1, 0, 0], angle = 0),]
             # Quaternion(axis=[0, 1, 0], angle = np.pi/2)]

def main():
    parser = argparse.ArgumentParser(description = ('Tests `SimpleBuilder` '+\
                                                   'and associated classes'))

    parser.add_argument('out', type = str, help = 'Path to save render.')
    args = parser.parse_args()

    print('creating starting tower')
    base_dims = [10, 10]
    empty_tower = EmptyTower(base_dims)
    print('creating block for building')
    block_dims = [2, 1, 1]
    block = SimpleBlock(block_dims)

    max_blocks = 200
    max_height = 100
    builder = SimpleBuilder(max_blocks, max_height)

    new_tower = builder(empty_tower, block, rotations)

    tower_json = repr(new_tower)

    pprint.pprint(json.loads(repr(new_tower)))
    # pprint.pprint(tower_json)
    # print(pprint.pprint(json.loads(json.dumps(tower_json, cls=TowerEncoder))))
    # json_io = io.BytesIO(json.dumps(tower_json))

    scene = BlockScene(tower_json)
    img_out = os.path.join(args.out, 'test_render')
    scene.render(img_out, [1])
    scene_out = os.path.join(args.out, 'test_scene.blend')
    scene.save(scene_out)

if __name__ == '__main__':
    main()
