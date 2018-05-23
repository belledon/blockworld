import numpy as np
import networkx as nx
from towers.tower import Tower

class EmptyTower(Tower):

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
    def base_dimensions(self):
        return self.blocks['base']['dims']

    @base_dimensions.setter
    def base_dimensions(self, ds):

        if len(ds) != 2:
            msg = 'Dimensions of length {0:d} not accepted'.format(len(ds))
            raise ValueError(msg)

        ds = np.array(ds)
        g = nx.DiGraph()
        g.add_node('base', block = blocks.BaseBlock(ds))
        self._blocks = g


    @property
    def blocks(self):
        return self._blocks

    # Methods #

    def __len__(self):
        return 0

    def available_surface(self):
        """
        Returns surface maps valid for block placement.

        Empty towers return their base as a flat surface.
        """
        surface = self.blocks['base']['blocks'].surface()
        return [surface]

    def place_block(self, block, parent, position, orientation):
        """
        Returns a new tower with the given blocked added.
        """
        g = self.base
        g.add_node(1, block = block, position, orientation)
        g.add_edge('base', 1)
        new_tower = towers.SomeTower(g)
        return new_tower


    def is_stable(self):
        """
        An empty tower is always considered stable.
        """
        return True

    def serialize(self):
        return {'base' : self.blocks['base']['block'].serialize()}
