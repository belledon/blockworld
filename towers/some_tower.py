import numpy as np
import networkx as nx
from towers.tower import Tower

class SomeTower(Tower):

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
        return self._blocks

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


    # Methods #

    def __len__(self):
        return len(self.blocks) - 1

    def available_surface(self):
        """
        Returns surface maps valid for block placement.
        """
        g = self.blocks

        # find the top-most blocks
        tops = [block for block in g if len(g.succesors(b) == 0)]

        # get the top surface of each block
        blocks = g.successors('base')
        for b_id in blocks:
            block = g[b_id]
            position = block['position']
            orientation = block['orientation']
            surface = block['block'].surface(orientation)
            # adjust the object-relative plane by its position in the tower
            adjusted = surface + position
            surfaces.append(surface)

        # sort by height (max -> min)
        zs = np.array([s[0,3] for s in surfaces])
        order = np.argsort(zs, order='descending')
        return surfaces[order]

    def place_block(self, block, parent, position, orientation):
        """
        Returns a new tower with the given blocked added.
        """
        g = self.base
        g.add_node(1, block = block)
        g.add_edge('base', 1)
        new_tower = towers.SomeTower(g)
        return new_tower


    def is_stable(self):
        """
        An empty tower is always considered stable.
        """
        return True

    def serialize(self):
        g = self.blocks
        return {b : b['block'].serialize for b in g}
