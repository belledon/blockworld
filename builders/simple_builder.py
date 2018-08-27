import copy
import pprint
import functools
import numpy as np

from shapely import geometry, affinity
# from shapely.prepared import prep

from utils import math_2d, geotools
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

    def __init__(self, max_blocks, max_height = 100):
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



    def find_placements(self, tower, block):
        """
        Enumerates the geometrically valid positions for
        a block surface on a tower surface.

        This is done in three stages:

        1) Enumeration:
         First, an grid is defined over the tower base.
         This grid represents all possible points in an
         xy plane.

         Next, the z-normal xy planes of the tower are aggregated into
         polygon collections (tower levels), where any xy planes residing on
         the same z-axis belong to the same collection.

         Finally, find the intersect between the xy grid and each tower level.

        2) Proposition:
         For each tower level-grid intersect, determine if placing the given
         block at the point causes a collision.

        3) Stability Evalutation:
         For each non-colliding point on the grid, determine if the placement
         would be locally stable (algorithm describing in `geotools` module).

        The "parents" of a block are defined as any block that supports the
        stability of the proposed placement.

        Arguments:
           tower (`Tower`): Base to build on
           block_dims (`np.ndarray`): Dimensions of new block
           stability (bool): If `True`, ensures global stability (False).

        Returns:
           An list of tuples of the form [(`Parent`, position)..]

        The tower surfaces are expected to be sorted along the
        z-axis.
        """
        positions = []
        parents = []
        # The base of the tower
        base_grid = geotools.make_grid(tower.base)
        all_blocks, levels = tower.levels()
        # Each z-normal surface currently available on the tower
        for (level_z, level_blocks) in levels:

            block_ids, blocks = zip(*level_blocks)
            # defining the layer
            block_z_surfaces = [b.surface for b in blocks]
            # Create a collection of polygons describing this z-slice
            layer = geometry.MultiPolygon(block_z_surfaces)
            # Find the intersect between the grid of possible points and z-layer
            grid = base_grid.intersection(layer.envelope)
            # Find all points on grid where the new block would not collide
            proposals = geotools.propose_placements(block, grid, level_z)

            locally_stable_f = lambda p : geotools.local_stability(p, layer)
            locally_stable = list(filter(locally_stable_f, proposals))

            collision_f = lambda p : all(
                map(lambda b : not p.collides(b), all_blocks))
            no_collision = list(filter(collision_f, locally_stable))

            level_parents = [[i for i,b in level_blocks if pot.isparent(b)]
                             for pot in no_collision]

            positions.extend(no_collision)
            parents.extend(level_parents)

        return zip(parents, positions)

    def __call__(self, base_tower, blocks, stability = True):
        """
        Builds a tower ontop of the given base.

        Follows the constrains given in `max_blocks` and `max_height`.
        """

        t_tower = copy.deepcopy(base_tower)

        for ib, block in enumerate(blocks):
            if t_tower.height >= self.max_height:
                break

            print('BLOCK', ib)
            valids = list(self.find_placements(t_tower, block))
            if len(valids) == 0:
                print('Could not place any more blocks')
                break
            parents, b = valids[np.random.choice(len(valids))]
            t_tower = t_tower.place_block(b, parents)

        return t_tower
