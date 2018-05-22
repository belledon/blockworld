import networkx as nx
from abstract import ABC

class Tower(ABC):

    """
    Interface for towers.

    Towers describe the relational structure of a configuration
    of blocks.

    Relationships are encoded two types of undirected graphs:
    1) parent/child relationships
    2) neighbors.

    Parent/child relationships describe the building process where the
    parent is the block on which the child was placed.

    Neighbors are simply unintend, adjacent (touching) blocks. 

    Attributes:
        base_dimensions (tuple(float)): The dimensions of the base.
        blocks (`nx.Graph`(`Block`)): The blocks composing the tower.
        height (float): The heighest point on the tower(in world units).
    """

    # Properties #

    @property
    def base_dimensions(self):
        return self._base_dimensions

    @base_dimensions.setter
    def base_dimensions(self, ds):

        if len(ds) != 3:
            msg = 'Dimensions of length {0:d} not accepted'.format(len(ds))
            raise ValueError(msg)

        self._base_dimensions = np.array(ds)

    @property
    @abstractmethod
    def blocks(self):
        pass

    @property
    @abstractmethod
    def height(self):
        pass


    # Methods #

    @abstractmethod
    def is_stable(self):
        """
        Evaluates the stability of the tower (if collapses).
        """
        pass

    @abstractmethod
    def serialize(self):
        """ Serializes the tower to `dict` """
        pass
