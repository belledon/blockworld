import copy
import pprint
import numpy as np

from . import block_scene

class TowerEntropy:

    """
    Performs "enotropy" analysis on towers.
    """

    def __init__(self, energy):
        self.structure = tower
        self.materials = materials


    @property
    def materials(self):
        return self._materials

    @materials.setter
    def materials(self, m):
        keys, vals = zip(*m.items())
        self._materials = list(keys)
        self._mat_ps = list(vals)

    @property
    def mat_ps(self):
        return self._mat_ps

    #-------------------------------------------------------------------------#


    #-------------------------------------------------------------------------#

    # Physics and movement

    def simulate(self, tower):
        """
        Controls simulations and extracts positions
        """
        scene = block_scene.BlockScene(tower, frames = 10)
        scene.bake_physics()
        trace = scene.get_trace(frames = [0, 10])
        return [t['position'] for t in trace]

    def movement(self, positions, eps = 1E-3):
        vel = np.abs((positions[-1] - positions[0]) / len(positions))
        print(np.mean(np.round(vel, 3)))
        return np.mean(np.round(vel, 3)) > eps

    #-------------------------------------------------------------------------#

    def __call__(self, tower, configurations):
        """
        Evaluates the stability of the tower at each block.

        Returns:
          - The randomly sampled congruent tower.
          - The stability results for each block in the tower.
        """
        d = [
            {'id' : 'template',
              'body' : tower,
              'entropy' : self.entropy(tower)}
        ]

        for (block_id, c_tower) in configurations:
            d.append(
                {
                    'id'      : '{0:d}'.format(block_id),
                    'body'    : c_tower,
                    'entropy' : self.entropy(tower)
                })

        return d
