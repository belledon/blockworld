#!/bin/python3
""" Generates towers for inspection.
"""

import os
import glob
import json
import pprint
import argparse

import numpy as np
import networkx as nx

from config import CONFIG
import towers
from scenes.generator import Generator


def main():
    parser = argparse.ArgumentParser(
        description = 'Renders the towers in a given directory')
    parser.add_argument('n', type = int, help = 'Number of towers to generate')
    parser.add_argument('b', type = int, help = 'The size of each tower.')
    parser.add_argument('--out', type = str, help = 'Path to save renders.',
                        default = 'towers')
    parser.add_argument('--base', type = str,
                        help = 'Path to base tower.')

    args = parser.parse_args()
    out_d = os.path.join(CONFIG['data'], args.out)
    if not os.path.isdir(out_d):
        os.mkdir(out_d)

    if args.base is None:
        base = (2,1)
    else:
        base = towers.simple_tower.load(args.base)

    materials = {'Wood' : 1.0}
    gen = Generator(materials, 'local')

    for i, (new_tower, alt) in enumerate(gen(base, k = args.b, n = args.n)):
        base_name = 'blocks_{0:d}_tower_{1:d}.json'.format(args.b, i)
        out = os.path.join(out_d, base_name)
        with open(out, 'w') as f:
            json.dump(new_tower.serialize(), f, indent=4, sort_keys = True)

if __name__ == '__main__':
    main()
