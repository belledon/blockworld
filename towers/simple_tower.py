import copy
import json
import numpy as np
import networkx as nx

from towers.tower import Tower
from utils.json_encoders import TowerEncoder

class SimpleTower(Tower):

    """
    Non-Empty instance of a `Tower`.


    Attributes:
        base_dimensions (tuple(float)): The dimensions of the base.
        blocks (`nx.Graph`(`Block`)): The graph describing the blocks composing
            the tower.
    """

    def __init__(self, blocks):
        self.blocks = blocks

    # Properties #

    @property
    def base_dimensions(self):
        return self.blocks['base']['dims']

    @property
    def blocks(self):
        return copy.deepcopy(self._blocks)

    @blocks.setter
    def blocks(self, blocks):

        if not isinstance(blocks, nx.DiGraph):
            msg = 'Type of given blocks is not valid.'
            raise ValueError(msg)

        if not 'base' in blocks:
            msg = 'Tower does not have a base.'
            raise ValueError(msg)

        if len(blocks) <= 1:
            msg = 'When trying to initialie an empty tower use '+\
                  '`towers.EmptyTower`.'
            raise ValueError(msg)

        self._blocks = blocks

    @property
    def height(self):

        g = self.blocks
        tops = [b for b in g if len(list(g.successors(b))) == 0]
        result = 0
        for top in tops:
            block = g.nodes[top]
            position = block['position']
            orientation = block['orientation']
            surface = block['block'].surface(orientation)
            # adjust the object-relative plane by its position in the tower
            adjusted = (surface + position)[0,2]
            result = max(adjusted, result)

        # used to adjust the total height
        base_height = g.nodes['base']['block'].dimensions[2]
        return result - base_height

    # Methods #

    def __len__(self):
        return len(self.blocks) - 1

    def available_surface(self):
        """
        Returns surface maps valid for block placement.
        """
        g = self.blocks
        # get the top surface of each block
        surfaces = []
        block_ids = list(g)
        for b_id in list(g):
            block = g.nodes[b_id]
            position = block['position']
            orientation = block['orientation']
            surface = block['block'].surface(orientation)
            # adjust the object-relative plane by its position in the tower
            adjusted = surface + position
            surfaces.append(adjusted)

        if len(surfaces) > 1:
            # sort by height (max -> min)
            zs = np.array([s[0,2] for s in surfaces])
            order = np.argsort(zs)[::-1]
            surfaces = np.array(surfaces)[order]
            block_ids = np.array(block_ids)[order]

        return list(zip(block_ids, surfaces))

    def place_block(self, block, parent, position, orientation):
        """
        Returns a new tower with the given blocked added.
        """
        g = self.blocks
        b_id = '{0:d}'.format(len(g))
        # adjust z axis by center of the object
        surface = block.surface(orientation)
        dz = surface[0,2]
        position = np.add(position, [0, 0, dz])
        g.add_node(b_id, block = block, position = position,
                   orientation = orientation)
        g.add_edge(parent, b_id)
        new_tower = SimpleTower(g)
        return new_tower


    def is_stable(self):
        """
        Returns `True` for now.
        Not sure if method will remain.
        """
        return True

    def serialize(self):
        g = self.blocks
        d = dict(id='id', children='children', block = 'block',
                 position='position',  orienatation='orienatation')
        return nx.tree_data(g, 'base', attrs=d)
        # return nx.jit_data(g)

    def __repr__(self):
        return json.dumps(self.serialize(), cls = TowerEncoder)
