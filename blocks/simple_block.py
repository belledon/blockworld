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

    def surface(self, orientation = Quaternion(), top = True, step=1.00):
        """
        Returns the surface plane.

        Defaults to the top surface along the z-axis.
        """
        mat = self.mat
        rotated = np.array([orientation.rotate(m) for m in mat])

        # find the top surface
        order = np.argsort(rotated[:, 2])
        corners = rotated[order[-4:]]
        # correct z axis
        delta = np.array([0, 0, abs(corners[0,2])])
        if not top:
            delta = delta * -1.0

        corners = corners + delta
        t = corners[np.argsort(corners[:, 1]), :2]
        t = t[np.argsort(t[:, 0])]
        xs = np.arange(t[0,0], t[2,0] + step, step)
        ys = np.arange(t[0,1], t[1,1] + step, step)
        zs = np.repeat(corners[0,2], len(xs) * len(ys))
        surface_t = np.array(np.meshgrid(xs, ys)).T.reshape(-1, 2)
        surface = np.hstack((surface_t, np.expand_dims(zs, axis=1)))
        return surface

    def serialize(self):
        """
        Serializes the attributes of the block to `dict`.
        """
        d = {'dims' : self.dimensions.tolist()}
        return d

    def __repr__(self):
        return self.serialize().__repr__()