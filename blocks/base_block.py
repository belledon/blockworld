from pyquaternion import Quaternion

from blocks.simple_block import SimpleBlock


class BaseBlock(SimpleBlock):

    """
    Interface for block objects.

    Attributes:
        dimensions (tuple(int)): The x,y,z dimensions of the block.
        mat (np.ndarray(float)): The matrix representing the box world.
        # candidates
        rendering (): Parameters used for rendering

    """

    # Properties #

    @property
    def dimensions(self):
        return self._dims

    @dimensions.setter
    def dimensions(self, ds)
        if len(ds) != 2:
            msg = 'Dimensions must have length 2'
            raise ValueError(msg)
        t = np.zeros(3)
        t[:2] = np.array(ds)
        self._dims = t
        self._mat = t

    @property
    def orientation(self):
        return Quaternion()


    # Methods #

    def surface(self):
        """
        Returns the surface plane.

        Defaults to the top surface along the z-axis.
        """
        rot = Quaternion()

        return super(BaseBlock, self).surface(rot)
