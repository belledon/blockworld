import copy
import pprint
import numpy as np
from scipy.spatial import ConvexHull
from shapely import geometry, affinity
from shapely.prepared import prep

from utils import math_2d
from builders.builder import Builder

# import matplotlib as mpl
# mpl.use('Agg')
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle, Wedge, Polygon
import matplotlib.pyplot as plt


def plot_coords(ax, ob):
    # x, y = ob.xy
    print(np.array(list(ob.coords)).shape)
    # xy = np.array(list(ob.xy))
    pgon = Polygon(np.array(list(ob.coords)))
    p = PatchCollection([pgon], alpha=0.4)
    colors = 100*np.random.rand(1)
    p.set_array(np.array(colors))
    ax.add_collection(p)
    # ax.plot(x, y, 'o', color='#999999', zorder=1)



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

    def make_grid(self, bbox, step = 0.25):
        xs = np.arange(bbox[0], bbox[2] + step, step)
        ys = np.arange(bbox[1], bbox[3] + step, step)
        grid = np.array(np.meshgrid(xs, ys)).T.reshape(-1, 2)
        return geometry.MultiPoint(grid)


    def find_placement(self, tower_surface, block_dims):
        """
        Enumerates the geometrically valid positions for
        a block surface on a tower surface.

        The tower surfaces are expected to be sorted along the
        z-axis.
        """
        print('FINDING PLACEMENT')
        dx,dy,_ = block_dims
        exclude = geometry.Polygon()
        positions = []
        parents = []
        bounds = [np.hstack((np.min(cs[:,:2],axis=0), np.max(cs[:,:2],axis=0)))
                            for _,cs in tower_surface]
        planes = [geometry.box(*bs) for bs in bounds]


        for row, (parent, corners) in enumerate(tower_surface):
            # only consider x-y plane
            print('on parent', parent)
            bbox = bounds[row]
            z = corners[0, 2]

            grid = self.make_grid(bbox)
            plane = planes[row]
            print('starting grid', len(grid))
            # skim off any points near the edge
            safe_plane = affinity.scale(plane, 0.9, 0.9)

            grid = geometry.MultiPoint(
                list(filter(safe_plane.contains, grid)))
            print('after safe trimming', len(grid))
            # only consider points that are stable
            for lower_plane in planes[row+1:]:
                if len(grid) < 1:
                    continue
                print('lower_plane', lower_plane.bounds)
                grid = geometry.MultiPoint(
                    list(filter(lower_plane.contains, grid)))

            print('after stability', len(grid))
            if len(grid) < 1:
                continue

            # removed points already used by higher planes
            for higher_plane in planes[:row]:
                if len(grid) < 1:
                    continue
                p_bounds = higher_plane.bounds
                # print(list(cv_hull.exterior.coords))
                ddx = 1 + dx / (p_bounds[2] - p_bounds[0])
                ddy = 1 + dy / (p_bounds[3] - p_bounds[1])
                hp_scaled = affinity.scale(higher_plane, ddx, ddy)
                to_exclude = geometry.MultiPoint(
                    list(filter(hp_scaled.contains, grid)))
                grid = grid.difference(to_exclude)
                print('to exclude', len(to_exclude))
                print(to_exclude)
                print('after exclusion', len(grid))
            if len(grid) < 1:
                continue

            # store good points and associated parent ids
            passed = np.empty((len(grid), 3))
            passed[:,:2] = np.vstack([p.coords for p in grid])
            passed[:,2] = z

            positions += passed.tolist()
            parents += np.repeat(parent, len(grid)).tolist()

            # exclude borders for following surfaces
            # cv_hull = geometry.MultiPoint(filtered).convex_hull

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

        print('randomly generated ', len(valid))
        return valid

    def __call__(self, base_tower, block, rotations):
        """
        Builds a tower ontop of the given base.

        Follows the constrains given in `max_blocks` and `max_height`.
        """

        t_tower = copy.deepcopy(base_tower)

        for ib in range(self.max_blocks):
            if t_tower.height >= self.max_height:
                break

            valids = self.valid_placements(t_tower, block, rotations)
            parent, pos, rot = valids[np.random.choice(len(valids))]
            t_tower = t_tower.place_block(block, parent, pos, rot)

        return t_tower
