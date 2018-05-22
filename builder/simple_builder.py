import numpy as np
import scipy.spatial

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

    # Properties #

    @property
    @abstractmethod
    def max_blocks(self):
        pass

    @property
    @abstractmethod
    def max_height(self):
        pass

    # Methods #

    def is_stable(self, tower_block, new_block):


    def find_placement(self, tower_surface, block_surface):
        """
        Enumerates the geometrically valid positions for
        a block surface on a tower surface.

        The tower surfaces are expected to be sorted along the
        z-axis.
        """
        dx,dy = (block_surface / 2.0)
        exclude = []
        positions = []
        for ranked_plane in tower_surface:
            # only consider x-y plane
            points = ranked_plane[:, :2]
            z = ranked_plane[0, 2]

            # removed points already used by higher planes
            filtered = np.array([p for p in points
                        if not any(np.isclose(point, exluded))])
            passed = np.empty((len(filtered), 3))
            passed[:,:2] = filtered
            passed[:,2] = z
            positions = np.hstack(positions, passed)

            # find 
            cv_hull = ConvexHull(filtered)
            center = np.mean(cv_hull, axis = 1)

            rots = cv_hull - center
            rots = rots / np.linalg.norm(rots)
            expanded = cv_hull + np.vstack([np.cos(rots.T[0]) * dx,
                                           np.sin(rots.T[1]) * dy]).T
            exclude = np.hstack(exclude, expanded)

        return positions

    def valid_placements(self, tower, block):
        """
        Finds suitable placements for a block on a tower.
        """
        block_surfaces = block.surfaces()
        tower_surface = tower.available_surface()

        valid = []
        for block_surface in block_surfaces:
            area = block_surface['area']
            positions = self.evaluate_placement(tower_surface, area)
            rot = block_surface['orientation']
            results = [(pos, rot) for pos in positions]
            valid.append(results)

        return valid

    @abstractmethod
    def __call__(self, base_tower, block=None):
        """
        Builds a tower ontop of the given base.

        Follows the constrains given in `max_blocks` and `max_height`.
        """

        if block is None:
            block = blocks.SimpleBlock()

        t_tower = copy.deepcopy(base_tower)

        for ib in range(self.max_blocks):

            if t_tower.height >= self.max_height:
                return t_tower

            valids = self.valid_placements(t_tower, block)
            pos, rot = np.random.choice(valids)
            t_tower = t_tower.place_block(block, pos, rot)

        return t_tower
