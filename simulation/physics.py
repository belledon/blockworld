import copy
import pprint
import numpy as np

import towers
import blocks
from . import block_scene

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
        scene = block_scene.BlockScene(tower_s, frames = self.frames)
        scene.bake_physics()
        trace = scene.get_trace(frames = np.arange(self.frames))
        return np.array([t['position'] for t in trace])

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
        vel = np.mean(np.sum(velocity(positions), axis = 0), axis = 1)
        phys_params = tower.extract_feature('substance')
        density  = np.array([d['density'] for d in phys_params])
        volume = np.array([np.prod(tower.blocks[i+1]['block'].dimensions)
                           for i in range(len(tower))])
        mass = density * volume
        # sum the vel^2 for each object across frames
        ke = 0.5 * mass * np.square(vel)
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
    tower_d = tower.serialize()
    for block_i in range(len(tower)):
        block = tower.blocks[block_i + 1]['block']
        new_pos = block.pos + deltas[block_i]
        tower_d[block_i + 1]['data']['pos'] = new_pos

    new_tower = towers.simple_tower.load(tower_d)
    return new_tower
