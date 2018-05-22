from abstract import ABC, abstractmethod


class Builder(ABC):

    """
    Interface for tower builder.

    Given a tower (may be empty), iteratively stacks blocks until the given
    criteria for completion has been met.

    Attributes:
        max_blocks (int): The maximum number of blocks to be added.
        max_height (int): The maximum height to be added.

    """

    # Properties #

    @property
    @abstractmethod
    def max_blocks(self):
        pass

    @property
    @abstractmethod
    def max_height(self):
        pass

    # Methods #

    @abstractmethod
    def valid_placements(self, tower, block):
        """
        Finds suitable placements for a block on a tower.
        """
        pass

    @abstractmethod
    def __call__(self, base_tower):
        """
        Builds a tower ontop of the given base.

        Follows the constrains given in `max_blocks` and `max_height`.
        """
        pass
