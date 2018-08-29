#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Generates user-specific config for current project.
'''

import os
import yaml
import errno
import argparse

d_data = 'data'
d_singularity = 'singularity/env.simg'
config_path = 'config.yaml'


class Config:

    """
    Stores project config
    """

    def __init__(self):
        if not os.path.isfile(config_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                    config_path)

        with open(config_path, 'r') as f:
            d = yaml.safe_load(f)
        self.d = d

    def __getitem__(self, k):
        return self.d[k]

CONFIG = Config()


def user_input(msg):
    msg = '{0!s} (y/n)'.format(msg)
    c = input(msg)
    if c == 'y':
        return True
    elif c == 'n':
        return False
    else:
        print('Did not recognize response')
        user_input()



def main():

    parser = argparse.ArgumentParser(
        description = 'Creates a user specifc config')

    parser.add_argument('--data', type = str, default = d_data,
                        help = 'Path to store project data.')
    parser.add_argument('--singularity', type = str, default = d_singularity,
                        help = 'Path to singularity container')
    args = parser.parse_args()

    if not os.path.isdir(d_data):
        print('Storing data at {0!s}'.format(args.data))
        os.mkdir(args.data)

    c = {
        'data' : args.data,
        'env' : args.singularity
    }

    if os.path.isfile(config_path):
        msg = 'Config file already exists. Over write?'
        if user_input(msg):
            print('overwriting')
            with open(config_path, 'w') as f:
                yaml.dump(c, f)
    else:
        with open(config_path, 'w') as f:
            yaml.dump(c, f)


if __name__ == '__main__':
    main()
