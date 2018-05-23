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
    def dimensions(self, ds)
        if len(ds) != 3:
            msg = 'Dimensions of length {0:d} not accepted'.format(len(ds))
            raise ValueError(msg)

        ds = np.array(ds)
        self._dims = ds
        self._mat = ds

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
    def orientation(self, or):
        if len(or) != 4:
            msg = 'Dimensions of orientation are not valid. Expected 4.'
            raise ValueError(msg)

        self._orientation = Quaternion(orientation)

    # Methods #

    def surface(self, top = True):
        """
        Returns the surface plane.

        Defaults to the top surface along the z-axis.
        """
        mat = self.mat
        rotated = self.orientation.rotate(mat)

        # find the top surface
        order = np.argsort(rotated[:, 2])
        corners = rotated[order[-4:]]

        # correct z axis
        delta = np.array([0, 0, abs(corners[0,2])])
        if not top:
            delta = delta * -1.0

        corners = corners + delta

        t = np.sort(corners, axis =0)
        t = np.sort(t, axis = 1)
        xs = np.arange(t[0,0], t[2,0] + 0.25, 0.25)
        ys = np.arange(t[0,1], t[1,1] + 0.25, 0.25)
        zs = np.repeat(t[0,2], len(xs))
        surface = np.array(np.meshgrid(xs, ys, zs)).T
        return surface.reshape(-1, 3)


    def serialize(self):
        """
        Serializes the attributes of the block to `dict`.
        """
        d = {'dims' = self.dims}
        return d
