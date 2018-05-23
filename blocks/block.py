from abstract import ABC


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
    def orientation(self):
        pass

    # Methods #

    @abstractmethod
    def surfaces(self):
        """
        Returns each surface as a plane.
        """
        pass

    @abstractmethod
    def serialize(self):
        """
        Serializes the attributes of the block to `dict`.
        """
        pass
