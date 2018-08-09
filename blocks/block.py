from abc import ABC, abstractmethod


class Block(ABC):

    """
    Interface for block objects.

    Attributes:
        dimensions (tuple(int)): The x,y,z dimensions of the block.
        orientation (tuple(float)) : The 4d quaternion describing orientation.

        # candidates
        rendering (): Parameters used for rendering

    """

    # Properties #

    @property
    @abstractmethod
    def dimensions(self):
        pass

    @property
    @abstractmethod
    def mat(self):
        pass

    # Methods #

    @abstractmethod
    def surface(self):
        """
        Returns the surface plane of either the top or bottom face.
        """
        pass

    @abstractmethod
    def serialize(self):
        """
        Serializes the attributes of the block to `dict`.
        """
        pass
