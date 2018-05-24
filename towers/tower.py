from abc import ABC, abstractmethod

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
    @abstractmethod
    def base_dimensions(self):
        pass

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
    def available_surface(self):
        """
        Returns surface maps valid for block placement.
        """
        pass

    @abstractmethod
    def place_block(self):
        """
        Returns a new tower with the given blocked added.
        """
        pass

    # @abstractmethod
    # def is_stable(self):
    #     """
    #     Evaluates the stability of the tower (if collapses).
    #     """
    #     pass

    @abstractmethod
    def serialize(self):
        """ Serializes the tower to `dict` """
        pass
