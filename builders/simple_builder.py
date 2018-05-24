import copy
import pprint
import numpy as np
from scipy.spatial import ConvexHull
from shapely import geometry

from utils import math_2d
from builders.builder import Builder


class SimpleBuilder(Builder):

    """
    Interface for tower builder.

    Given a tower (may be empty), iteratively stacks blocks until the given
    criteria for completion has been met.

    Attributes:
        max_blocks (int): The maximum number of blocks to be added.
        max_height (int): The maximum height to be added.

    """

    def __init__(self, max_blocks, max_height):
        self.max_blocks = max_blocks
        self.max_height = max_height


    # Properties #

    @property
    def max_blocks(self):
        return self._max_blocks

    @max_blocks.setter
    def max_blocks(self, v):
        v = int(v)
        if v <= 0 :
            msg = '`max_blocks` must be greater than 0'
            raise ValueError(msg)
        self._max_blocks = v

    @property
    def max_height(self):
        return self._max_height

    @max_height.setter
    def max_height(self, v):
        v = int(v)
        if v <= 0 :
            msg = '`max_height` must be greater than 0'
            raise ValueError(msg)
        self._max_height = v

    # Methods #

    def find_placement(self, tower_surface, block_dims):
        """
        Enumerates the geometrically valid positions for
        a block surface on a tower surface.

        The tower surfaces are expected to be sorted along the
        z-axis.
        """
        dx,dy,_ = block_dims / 2.0
        exclude = geometry.Polygon()
        positions = []
        parents = []
        for parent, plane in tower_surface:
            # only consider x-y plane
            points = plane[:, :2]
            z = plane[0, 2]

            points = geometry.MultiPoint(points)
            # removed points already used by higher planes
            filtered = points.difference(exclude)
            # print(filtered)
            # store good points and associated parent ids
            passed = np.empty((len(filtered), 3))
            passed[:,:2] = np.vstack([p.coords for p in filtered])
            passed[:,2] = z

            positions += passed.tolist()
            parents += np.repeat(parent, len(filtered)).tolist()

            # exlcude borders for following surfaces
            # cv_hull = np.array(math_2d.convex_hull(filtered))
            # cv_hull = filtered[ConvexHull(filtered).vertices]
            cv_hull = geometry.MultiPoint(filtered).convex_hull
            cv_hull_x = cv_hull.buffer(dx)
            cv_hull_y = cv_hull.buffer(dy)
            cv_hull_sd = cv_hull_x.symmetric_difference(cv_hull_y)
            cv_hull_complete = cv_hull.union(cv_hull_sd)
            # print(filtered)
            # print(cv_hull)
            # center = np.mean(cv_hull, axis = 1)
            # raise ValueError()
            # rots = cv_hull - center
            # rots = np.arctan(rots / np.linalg.norm(rots))
            # expanded = cv_hull + np.vstack([np.cos(rots.T[0]) * dx,
            #                                np.sin(rots.T[1]) * dy]).T
            exclude = exclude.union(cv_hull)

        parents = np.array(parents).flatten()
        return zip(parents, positions)

    def valid_placements(self, tower, block, rotations):
        """
        Finds suitable placements for a block on a tower.
        """
        # list of (parent, surface) tuples
        tower_surfaces = tower.available_surface()

        valid = []
        for rot in rotations:
            surface = block.surface(rot, False)
            block_dims = np.max(surface, axis = 0) - np.min(surface, axis = 0)
            positions = self.find_placement(tower_surfaces, block_dims)
            results = [(parent, pos, rot) for parent, pos in positions]
            valid += results

        return valid

    def __call__(self, base_tower, block, rotations):
        """
        Builds a tower ontop of the given base.

        Follows the constrains given in `max_blocks` and `max_height`.
        """

        t_tower = copy.deepcopy(base_tower)

        for ib in range(self.max_blocks):
            print('height', t_tower.height)
            print('blocks', len(t_tower), ib)
            if t_tower.height >= self.max_height:
                break

            valids = self.valid_placements(t_tower, block, rotations)
            parent, pos, rot = valids[np.random.choice(len(valids))]
            t_tower = t_tower.place_block(block, parent, pos, rot)

        return t_tower
