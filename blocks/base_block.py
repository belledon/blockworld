import numpy as np
from pyquaternion import Quaternion

from blocks.simple_block import SimpleBlock


class BaseBlock(SimpleBlock):

    """
    Instance of `SimpleBlock` designed act as the tower base.

    Attributes:
        dimensions (tuple(int)): The x,y,z dimensions of the block.
        mat (np.ndarray(float)): The matrix representing the box world with a
            fixed height of 1.
        # candidates
        rendering (): Parameters used for rendering

    """

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
