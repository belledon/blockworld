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
        self.graph = blocks

    # Properties #

    @property
    def base_dimensions(self):
        return self.base.dimensions

    @property
    def base(self):
        return self.blocks[0]['block']

    @property
    def blocks(self):
        return self.graph.nodes

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, blocks):

        if not isinstance(blocks, nx.DiGraph):
            msg = 'Type of given blocks is not valid.'
            raise ValueError(msg)

        if not 0 in blocks:
            msg = 'Tower does not have a base.'
            raise ValueError(msg)

        if len(blocks) <= 1:
            msg = 'When trying to initialize an empty tower use '+\
                  '`towers.EmptyTower`.'
            raise ValueError(msg)

        self._graph = blocks
        self.height = blocks

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, g):

        tops = [b for b in g if len(list(g.successors(b))) == 0]
        result = 0
        for top in tops:
            block = g.nodes[top]['block']
            result = max(block.mat[0,2], result)

        # used to adjust the total height
        base_height = self.base.mat[0,2]
        self._height = result - base_height

    # Methods #

    def __len__(self):
        return len(self.blocks) - 1

    def levels(self, block_ids = None):
        """
        Returns surface maps valid for block placement.
        """
        bs = self.blocks
        # get the top surface of each block
        if block_ids is None:
            block_ids = list(bs)

        blocks = [bs[b_id]['block'] for b_id in block_ids]

        zs = [b.mat[0,2] for b in blocks]
        layers = np.unique(zs)
        tz = list(zip(block_ids, blocks, zs))
        data = [(l, [(i,b) for i,b,z in tz if z == l]) for l in layers]
        return blocks, data

    def place_block(self, block, parents):
        """
        Returns a new tower with the given blocked added.
        """
        g = self.graph
        b_id = len(g)
        g.add_node(b_id, block = block)
        for parent in parents:
            g.add_edge(parent, b_id)
        new_tower = SimpleTower(g)
        return new_tower

    def get_stack(self, block_id):
        """
        Returns the parents of this block.
        """
        g = self.graph
        parents = list(nx.shortest_path(g, source = 0, target = block_id))
        return parents

    def is_stable(self):
        """
        Returns `True` for now.
        Not sure if method will remain.
        """
        return True

    def serialize(self):
        g = self.graph
        d = dict(source='source', target='target', name='id',
                 key='key', link='links', block = 'block')
        data = nx.node_link_data(g, attrs=d)
        return json.loads(json.dumps(data, cls = TowerEncoder))

    def __repr__(self):
        return json.dumps(self.serialize())

    def apply_feature(self, feature, values):
        """
        Applys a feature to a set of blocks in a tower
        """
        n_blocks = len(self)
        n_values = len(values)
        if n_blocks != n_values:
            raise ValueError('Block, values missmatch')

        tower = copy.deepcopy(self)
        for b_id in np.arange(n_blocks):
            tower.blocks[b_id + 1][feature] = values[b_id]

        return tower

    def extract_feature(self, feature):
        n_blocks = len(self)
        values = []
        tower = copy.deepcopy(self)
        for b_id in np.arange(n_blocks):
            values.append(tower.blocks[b_id+1][feature])
        return np.array(values)
