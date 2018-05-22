import networkx as nx
from towers.tower import Tower

class EmptyTower(Tower):

    """
    Empty instance of a `Tower`.

    Used for a base tower in `builders.Builder`

    Attributes:
        base_dimensions (tuple(float)): The dimensions of the base.
        blocks (`nx.Graph`(`Block`)): An empty graph
    """

    def __init__(self, base_dims):
        self.base_dimensions = base_dims

    # Properties #

    @property
    def blocks(self):
        return nx.Graph()

    # Methods #

    def is_stable(self):
        """
        An empty tower is always considered stable.
        """
        return True

    def serialize(self):
        return {[]}
