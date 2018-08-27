import numpy as np

from blocks.simple_block import SimpleBlock


class BaseBlock(SimpleBlock):

    """
    Instance of `SimpleBlock` designed act as the tower base.

    Attributes:
        dimensions (tuple(int)): The x,y dimensions of the base.
        mat (np.ndarray(float)): The matrix representing the box world with a
            fixed height of 1.
    """

    def __init__(self, dims):
        self.dimensions = dims
        self.pos = [0, 0, -0.5]

    # Properties #

    @property
    def dimensions(self):
        return self._dims

    @dimensions.setter
    def dimensions(self, ds):
        if len(ds) != 2:
            msg = 'Dimensions must have length 2'
            raise ValueError(msg)
        t = np.ones(3)
        t[:2] = np.array(ds)
        self._dims = t
        self.mat = t
