import numpy as np
import networkx as nx
from towers.tower import Tower

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

    @property
    def height(self):

        g = self.blocks
        tops = [b for b in g if len(g.successors(b)) == 0]
        result = 0
        for top in tops:
            block = g[top]
            position = block['position']
            orientation = block['orientation']
            surface = block['block'].surface(orientation)
            # adjust the object-relative plane by its position in the tower
            adjusted = (surface + position)[0,2]
            result = max(adjusted, result)

        # used to adjust the total height
        base_height = g['base']['block'].dimensions[2]
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
        for b_id in g:
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
        g = self.blocks
        b_id = len(g) - 1
        g.add_node(b_id, block = block, position = position,
                   orientation = orientation)
        g.add_edge(parent, 1)
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

        return nx.tree_data(g, attrs=d)
