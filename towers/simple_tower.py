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

        if not 0 in blocks:
            msg = 'Tower does not have a base.'
            raise ValueError(msg)

        if len(blocks) <= 1:
            msg = 'When trying to initialie an empty tower use '+\
                  '`towers.EmptyTower`.'
            raise ValueError(msg)

        self._blocks = blocks
        self.height = blocks

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, g):

        tops = [b for b in g if len(list(g.successors(b))) == 0]
        result = 0
        for top in tops:
            block = g.nodes[top]
            position = block['position']
            surface = block['block'].surface()
            # adjust the object-relative plane by its position in the tower
            adjusted = (surface + position)[0,2]
            result = max(adjusted, result)

        # used to adjust the total height
        base_height = g.nodes[0]['block'].dimensions[2]
        self._height = result - base_height

    # Methods #

    def __len__(self):
        return len(self.blocks) - 1

    def available_surface(self, block_ids = None):
        """
        Returns surface maps valid for block placement.
        """
        g = self.blocks
        # get the top surface of each block
        if block_ids is None:
            block_ids = list(g)

        surfaces = []
        for b_id in block_ids:
            block_node = g.nodes[b_id]
            block = block_node['block']
            # adjust the object-relative plane by its position in the tower
            adjusted = block.surface() + block_node['position']
            surfaces.append(adjusted)

        # sort by height (max -> min)
        if len(surfaces) > 1:
            zs = np.array([s[0,2] for s in surfaces])
            order = np.argsort(zs)[::-1]
            surfaces = np.array(surfaces)[order]
            block_ids = np.array(block_ids)[order]

        return list(zip(block_ids, surfaces))

    def place_block(self, block, parent, position):
        """
        Returns a new tower with the given blocked added.
        """
        g = self.blocks
        b_id = len(g)

        # adjust z axis by center of the object
        surface = block.surface()
        dz = surface[0,2]
        position = np.add(position, [0, 0, dz])

        # add node to graph
        g.add_node(b_id, block = block, position = position)
        g.add_edge(parent, b_id)
        new_tower = SimpleTower(g)
        return new_tower

    def get_stack(self, block_id):
        """
        Returns the parents of this block.
        """
        g = self.blocks
        parents = list(nx.shortest_path(g, source = 0, target = block_id))
        return parents

    def is_stable(self):
        """
        Returns `True` for now.
        Not sure if method will remain.
        """
        return True

    def serialize(self):
        g = self.blocks
        d = dict(source='source', target='target', name='id',
                 key='key', link='links', block = 'block',
                 position='position',  orienatation='orienatation')
        data = nx.node_link_data(g, attrs=d)
        return json.loads(json.dumps(data, cls = TowerEncoder))

    def __repr__(self):
        return json.dumps(self.serialize())
