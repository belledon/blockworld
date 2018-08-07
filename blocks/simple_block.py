import numpy as np
from pyquaternion import Quaternion

from blocks.block import Block

class SimpleBlock(Block):

    """
    Interface for block objects.

    Attributes:
        dimensions (tuple(int)): The x,y,z dimensions of the block.
        mat (np.ndarray(float)): The matrix representing the box world.
        # candidates
        rendering (): Parameters used for rendering

    """

    def __init__(self, dimensions):
        self.dimensions = dimensions

    # Properties #

    @property
    def dimensions(self):
        return self._dims

    @dimensions.setter
    def dimensions(self, ds):
        if len(ds) != 3:
            msg = 'Dimensions of length {0:d} not accepted'.format(len(ds))
            raise ValueError(msg)

        ds = np.array(ds)
        self.mat = ds
        self._dims = ds

    @property
    def mat(self):
        return np.copy(self._mat)

    @mat.setter
    def mat(self, ds):
        """
        Define the vectors representing each corner.
        Vectors are centered around 0.
        """
        t = np.array([ds / 2.0 , -1 * ds / 2.0]).T
        t = np.array(np.meshgrid(*t)).T.reshape(-1, 3)
        self._mat = t

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, rot):
        if len(rot) != 4:
            msg = 'Dimensions of orientation are not valid. Expected 4.'
            raise ValueError(msg)

        self._orientation = Quaternion(rot)

    # Methods #

    def surface(self, orientation = Quaternion()):
        """
        Returns the surface plane.

        Defaults to the top surface along the z-axis.
        """
        # orient matrix
        mat = self.mat
        rotated = np.array([orientation.rotate(m) for m in mat])

        # find the top surface
        order = np.argsort(rotated[:, 2])
        corners = rotated[order[-4:]]

        return corners


    def serialize(self):
        """
        Serializes the attributes of the block to `dict`.
        """
        d = dict(dims = self.dimensions.tolist())
        return d

    def __repr__(self):
        return repr(self.serialize())

