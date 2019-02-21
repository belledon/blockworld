import copy
import pprint
import numpy as np

from blockworld import towers, blocks
from blockworld.simulation import tower_scene

class TowerEntropy:

    """
    Performs "entropy" analysis on towers.
    """

    def __init__(self, noise = 0.5, dims = [0, 1], frames = 30):
        self.noise = noise
        self.dims = dims
        self.frames = frames

    #-------------------------------------------------------------------------#

    # Physics and movement

    def simulate(self, tower):
        """
        Controls simulations and extracts positions
        """
        tower_s = tower.serialize()
        keys = list(tower.blocks.keys())[1:]
        with tower_scene.TowerPhysics(tower_s) as scene:
            trace = scene.get_trace(self.frames, keys)
        return trace['position']

    def movement(self, positions, eps = 1E-3):
        vel = velocity(positions)
        return np.mean(np.round(vel, 3)) > eps

    def perturb(self, tower, n = 50):
        """
        Generates `n` tower perturbations where each block in the tower
        is randomly shifted by a guassian with std = `noise`.
        """
        return [shift(tower, self.noise) for _ in range(n)]

    # TODO clean up density and volume retrieval...
    def kinetic_energy(self, tower):
        """
        Computes the kinetic energy summed across each block
        for each time frame.
        """
        positions = self.simulate(tower)
        positions = positions[:self.frames]
        # for each frame, for each object, 1 vel value
        vel = velocity(positions).mean(axis = -1)
        phys_params = tower.extract_feature('substance')
        density  = np.array([d['density'] for d in phys_params])
        volume = np.array([np.prod(tower.blocks[i+1]['block'].dimensions)
                           for i in range(len(tower))])
        mass = np.expand_dims(density * volume, axis = -1)
        # sum the vel^2 for each object across frames
        ke = 0.5 * np.dot(np.square(vel), mass).flatten()
        return np.sum(ke)

    def analyze(self, tower):
        """
        Returns statistics (mean, std) over the KE of a tower
        under random perturbations.
        """
        perturbations = self.perturb(tower)
        kes = [self.kinetic_energy(p) for p in perturbations]
        return tuple((np.mean(kes), np.std(kes)))

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
              'ke' : self.analyze(tower)}
        ]

        if not configurations is None:
            for (block_id, c_tower) in configurations:
                d.append(
                    {
                        'id'      : '{0:d}'.format(block_id),
                        'body'    : c_tower,
                        'ke' : self.analyze(tower)
                    })

        return d

def velocity(positions):
    """
    Computes step-wise velocity.
    """
    return np.abs((positions[1:] - positions[:-1]) / len(positions))

def shift(tower, std):
    """
    Applies an xy shift to blocks in a tower.
    """
    deltas = np.zeros((len(tower), 3))
    deltas[:, 0:2] = np.random.normal(scale = std, size = (len(tower), 2))
    d = tower.serialize()
    for block, delta in zip(d[1:], deltas):
        block['data']['pos'] += delta

    new_tower = towers.simple_tower.load(d)
    return new_tower
