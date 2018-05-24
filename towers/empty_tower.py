import numpy as np
import networkx as nx
from pyquaternion import Quaternion

from towers.simple_tower import SimpleTower
from blocks.base_block import BaseBlock

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
    def base_dimensions(self):
        return self.blocks['base']['dims']

    @base_dimensions.setter
    def base_dimensions(self, ds):

        if len(ds) != 2:
            msg = 'Dimensions of length {0:d} not accepted'.format(len(ds))
            raise ValueError(msg)

        ds = np.array(ds)
        g = nx.DiGraph()
        base = BaseBlock(ds)
        g.add_node('base', block = base, position = [0, 0, 0.5],
                   orientation = Quaternion())
        self._blocks = g

    @property
    def height(self):
        return 0

    # Methods #

    # def available_surface(self):
    #     """
    #     Returns surface maps valid for block placement.

    #     Empty towers return their base as a flat surface.
    #     """
    #     g = self.blocks
    #     surface = g.nodes['base']['block'].surface()
    #     return [('base', surface)]


    def is_stable(self):
        """
        An empty tower is always considered stable.
        """
        return True
