import numpy as np
import networkx as nx

from blockworld.towers.simple_tower import SimpleTower
from blockworld.blocks.simple_block import SimpleBlock
from blockworld.blocks.base_block import BaseBlock

class EmptyTower(SimpleTower):

    """
    Empty instance of a `Tower`.

    Used for a base tower in `builders.Builder`

    Attributes:
        base_dimensions (tuple(float)): The dimensions of the base.
        blocks (`nx.Graph`(`Block`)): A graph with only one element, the base.
    """

    def __init__(self, base_dims):
        self.base_dimensions = base_dims

    # Properties #

    @property
    def base(self):
        return self.blocks[0]['block']

    @property
    def base_dimensions(self):
        return self.base.dimensions

    @base_dimensions.setter
    def base_dimensions(self, ds):
        g = nx.DiGraph()
        base = BaseBlock(ds)
        g.add_node(0, block = base)
        self._graph = g

    @property
    def height(self):
        return self.base.mat[0, 2]

    # Methods #
    # def levels(self, block_ids = None):
    #     """
    #     Returns surface maps valid for block placement.
    #     """
    #     data = [(self.base.mat[0,2], [(0, self.base)])]
    #     return ([self.base], data)
