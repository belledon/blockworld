import copy
import pprint
import numpy as np

from . import block_scene

class TowerEntropy:

    """
    Performs "entropy" analysis on towers.
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
        vel = velocity(positions)
        return np.mean(np.round(vel, 3)) > eps

    def kinetic_energy(self, tower, frames = 30):
        """
        Computes the kinetic energy summed across each block
        for each time frame.
        """
        positions = self.simulate(tower)[:frames]
        # for each frame, for each object, 1 vel value
        vel = np.mean(velocity(positions), axis = 1)
        mass  = tower.extract_feature('mass')
        # sum the vel^2 for each object across frames
        ke = 0.5 * mass * np.sum(np.square(mass), axis = 1)
        return np.sum(ke)


    #-------------------------------------------------------------------------#

    def __call__(self, tower, configurations = None):
        """
        Evaluates the stability of the tower at each block.

        Returns:
          - The randomly sampled congruent tower.
          - The stability results for each block in the tower.
        """
        d = [
            {'id' : 'template',
              'body' : tower,
              'ke' : self.kenetic_energy(tower)}
        ]

        if not configurations is None:
            for (block_id, c_tower) in configurations:
                d.append(
                    {
                        'id'      : '{0:d}'.format(block_id),
                        'body'    : c_tower,
                        'ke' : self.kenetic_energy(tower)
                    })

        return d

def velocity(positions):
    """
    Computes step-wise velocity.
    """
    return np.abs((positions[-1] - positions[0]) / len(positions))
