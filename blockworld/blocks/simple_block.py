import numpy as np
from shapely import geometry, affinity

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

    def __init__(self, dimensions, pos = None):
        self.dimensions = dimensions
        self.pos = pos

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
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, p):
        if p is None:
            self._pos = np.zeros(3)
        elif isinstance(p, geometry.Point):
            self._pos = np.array(p.coords).flatten()
        else:
            try:
                self._pos = np.array(p).flatten()
            except:
                raise ValueError('Unsupported type for `pos`')

    @property
    def mat(self):
        return self._mat + self.pos

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
    def surface(self):
        """
        Returns the `geometry.PolygonCollections` representation
        of the block.
        """
        # get the two xy planes in a clockwise order
        clock = [2,1,0,3]
        top = self.mat[:4, :2][clock].tolist()
        # must envelope to make valid rectangle
        plane = geometry.Polygon((top + top[:1])).envelope
        return plane

    @property
    def com(self):
        """
        Center of mass.
        """
        return geometry.Point(self.pos[:2])

    # Methods #

    def collides(self, other):
        """
        Returns true if `other` collides with `self`.
        """
        if not isinstance(other, Block):
            raise ValueError('Other must be `Block`')

        planes = self.surface.intersects(other.surface) and \
                 (not self.surface.touches(other.surface))

        t_f = lambda a,b : ((b[0] >= a[0]) and (b[0] < a[1])) or \
            (b[1] <= a[1] and b[1] > a[0])
        zs = t_f(self.mat[(-1, 0), 2], other.mat[(-1, 0), 2]) or \
             t_f(other.mat[(-1, 0), 2], self.mat[(-1, 0), 2])
        return planes and zs

    def isparent(self, other):
        """
        Returns true if `other` is the parent of `self`.
        """
        if not isinstance(other, Block):
            raise ValueError('Other must be `Block`')
        planes = self.surface.intersects(other.surface) and \
                 (not self.surface.touches(other.surface))

        zs = np.isclose(other.mat[0,2], self.mat[-1, 2])
        return planes and zs

    def moveto(self, point, z):
        """
        Returns a new block moved to that position with the same dimensions.
        """
        coords = np.zeros(3)
        coords[:2] = point.coords
        coords[2] = z + self.dimensions[2] / 2
        return SimpleBlock(self.dimensions, pos = coords)


    def serialize(self):
        """
        Serializes the attributes of the block to `dict`.
        """
        d = {
            'dims' : list(self.dimensions.astype(float)),
            'pos'  : list(self.pos.astype(float)),
        }
        return d

    def __repr__(self):
        return repr(self.serialize())
