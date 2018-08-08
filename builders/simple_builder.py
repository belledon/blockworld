import copy
import pprint
import numpy as np
from scipy.spatial import ConvexHull
from shapely import geometry, affinity
from shapely.prepared import prep

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

    def make_grid(self, bbox, step = 0.1):
        xs = np.arange(bbox[0], bbox[2] + step, step)
        ys = np.arange(bbox[1], bbox[3] + step, step)
        grid = np.array(np.meshgrid(xs, ys)).T.reshape(-1, 2)
        return geometry.MultiPoint(grid)


    def find_placement(self, tower, block_dims, stability):
        """
        Enumerates the geometrically valid positions for
        a block surface on a tower surface.

        Arguments:
           tower (`Tower`): Base to build on
           block_dims (`np.ndarray`): Dimensions of new block
           stability (bool): If `True`, ensures global stability (False).

        Returns:
           An list of tuples of the form [(`Parent`, position)..]

        The tower surfaces are expected to be sorted along the
        z-axis.
        """
        dx,dy,_ = block_dims
        block_z = block_dims[2] * 2
        positions = []
        parents = []

        # The base of the tower
        base_grid = self.make_grid(tower.base)
        # Each z-normal surface currently available on the tower
        tower_layers = tower.available_surface()

        for (layer_z, blocks) in tower_surface:

            block_ids, block_geos = zip(*blocks)

            # defining the layer
            block_z_surfaces = [b.surface[0] for b in block_geos]
            layer = functools.reduce(lambda x,y : x.union(y), block_z_surfaces)

            proposals = [propose_placement(p, layer_z)]

            locally_stable_f = lambda p : local_stability(p, layer)
            locally_stable = filter(locally_stable_f, proposals)

            collision_f = lambda p : not any(
                map(lambda b : collides(p, b), all_blocks))







            # store valid points and associated parent ids
            if len(grid) > 0:
                coords = np.round(np.vstack([p.coords for p in grid]), 1)
                passed = np.empty((len(grid), 3))
                passed[:,:2] = coords
                passed[:,2] = z

                positions += passed.tolist()
                parents += np.repeat(parent, len(grid)).tolist()

        parents = np.array(parents).flatten()
        return zip(parents, positions)

    def valid_placements(self, tower, block, stability):
        """
        Finds suitable placements for a block on a tower.
        """
        surface = block.surface()
        block_dims = np.max(surface, axis = 0) - np.min(surface, axis = 0)
        block_dims[2] = surface[0, 2]
        placements = self.find_placement(tower, block_dims, stability)
        return list(placements)

    def __call__(self, base_tower, blocks, stability = True):
        """
        Builds a tower ontop of the given base.

        Follows the constrains given in `max_blocks` and `max_height`.
        """

        t_tower = copy.deepcopy(base_tower)

        for ib, block in enumerate(blocks):
            if t_tower.height >= self.max_height:
                break

            valids = self.valid_placements(t_tower, block, stability)
            if len(valids) == 0:
                print('Could not place any more blocks')
                break
            parent, pos = valids[np.random.choice(len(valids))]
            t_tower = t_tower.place_block(block, parent, pos)

        return t_tower
