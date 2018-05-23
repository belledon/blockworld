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
        parents = []
        for parent, plane in tower_surface:
            # only consider x-y plane
            points = plane[:, :2]
            z = plane[0, 2]

            # removed points already used by higher planes
            filtered = np.array([p for p in points
                        if not any(np.isclose(point, exluded))])
            # store good points and associated parent ids
            passed = np.empty((len(filtered), 3))
            passed[:,:2] = filtered
            passed[:,2] = np.repeat(z, len(filtered))
            positions = np.hstack(positions, passed)
            parents.append(np.repeat(parent, len(filtered)))

            # exlcude borders for following surfaces
            cv_hull = ConvexHull(filtered)
            center = np.mean(cv_hull, axis = 1)

            rots = cv_hull - center
            rots = np.arctan(rots / np.linalg.norm(rots))
            expanded = cv_hull + np.vstack([np.cos(rots.T[0]) * dx,
                                           np.sin(rots.T[1]) * dy]).T
            exclude = np.hstack(exclude, expanded)

        parents = np.array(parents).flatten()
        return zip(parents, positions)

    def valid_placements(self, tower, block, rotations):
        """
        Finds suitable placements for a block on a tower.
        """
        block_surfaces = [block.surface(r, False) for r in rotations]
        # list of (parent, surface) tuples
        tower_surfaces = tower.available_surface()

        valid = []
        for rot, block_surface in zip(rotations, block_surfaces):
            positions = self.evaluate_placement(tower_surfaces, block_surface)
            results = [(pos, rot) for pos in positions]
            valid.append(results)

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
            parent, pos, rot = np.random.choice(valids)
            t_tower = t_tower.place_block(block, parent, pos, rot)

        return t_tower
