#!/bin/python3

import os
import json
import pprint
import argparse
import numpy as np

from scenes.generator import Generator
from scenes import block_scene


def simulate_tower(tower, name, path):
    """
    Helper function that processes a tower.
    """
    tower_s = tower.serialize()
    tower_json = json.dumps(tower_s)
    json_path = os.path.join(path, name + '.json')
    with open(json_path, 'w') as f:
        json.dump(tower_s, f, indent = 4, sort_keys = True)

    scene = block_scene.BlockScene(tower_json, wire_frame = True)
    render_path = os.path.join(path, 'renders')
    if not os.path.isdir(render_path):
        os.mkdir(render_path)
    img_out = os.path.join(render_path, name)
    # scene.render(img_out, [1], resolution = (256, 256))
    # scene.render_circle(img_out, resolution = (128, 128), dur = 3)
    scene_out = os.path.join(path, name + '.blend')
    scene.save(scene_out)


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

    out = os.path.join(args.out, 'generator_test_output')
    if not os.path.isdir(out):
        os.mkdir(out)

    base = (2,1)
    # materials = {'Wood' : 0.5,
    #              'Metal': 0.5}
    materials = {'Wood' : 1.0}

    gen = Generator(base, args.number, materials, args.stability)

    for i, (new_tower, alt) in enumerate(gen(n = 5)):

        base_name = 'blocks_{0:d}_tower_{1:d}'.format(args.number, i)
        simulate_tower(new_tower, base_name, out)

        # for j, b_towers in enumerate(alt):
        #     b_tower_name = '{0!s}_block_{1:d}'.format(base_name, j)
        #     for mat in b_towers:
        #         m_tower_name = '{0!s}_mat_{1!s}'.format(b_tower_name, mat)
        #         cong, icon = b_towers[mat]
        #         c_name = m_tower_name + '_con'
        #         simulate_tower(cong, c_name, out)
        #         i_name = m_tower_name + '_inc'
        #         simulate_tower(icon, i_name, out)


if __name__ == '__main__':
    main()
