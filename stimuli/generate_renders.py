#!/bin/python3

import os
import json
import pprint
import argparse
import numpy as np

from scenes.generator import Generator
from scenes import block_scene

def main():
    parser = argparse.ArgumentParser(description = ('Tests `Generator` '+\
                                                   'and associated classes'))

    parser.add_argument('out', type = str, help = 'Path to save render.')
    parser.add_argument('--number', type = int, default = 10,
                        help = 'Number of blocks.')
    parser.add_argument('--stability', type = str, default = 'local',
                        choices = ['local', 'glocal'],
                        help = 'Height of the tower.')

    args = parser.parse_args()

    base = (2,1)
    materials = {'Wood' : 0.5,
                 'Metal': 0.5}

    gen = Generator(base, args.number, materials, args.stability)

    for (new_tower, alt) in gen():

        tower_json = json.dumps(new_tower)
        pprint.pprint(new_tower)

        with open(os.path.join(args.out, 'test.json'), 'w') as f:
            json.dump(new_tower, f, indent = 4, sort_keys = True)

        scene = block_scene.BlockScene(tower_json)
        img_out = os.path.join(args.out, 'renders/test_render')
        # scene.render(img_out, [1])
        scene.render_circle(img_out, resolution = (128, 128), dur = 3)
        scene_out = os.path.join(args.out, 'test_scene.blend')
        scene.save(scene_out)

if __name__ == '__main__':
    main()
