import pprint
import numpy as np
from . import block_scene

class TowerTester:

    """
    Controls search over a tower structure.
    """

    def __init__(tower, materials):
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
        return self._map_ps

    #-------------------------------------------------------------------------#

    # Material assignment and sampling

    def sample_tower(self):
        """
        Randomly assigns materials to a tower structure.
        """
        temp_tower = copy.copy(self.structure)
        blocks = temp_tower['nodes']
        n_blocks = len(blocks)
        materials = np.random.choice([1, 0],
                                     size = n_blocks,
                                     p = self.mat_ps)

        blocks = apply_feature(blocks, 'material', materials)
        blocks = apply_feature(blocks, 'congruency', bool(np.ones(n_blocks)))
        temp_tower['nodes'] = blocks
        return temp_tower


    def configurations(self, tower):
        """
        Generator for different tower configurations.
        """
        n_blocks = len(tower['nodes']) - 1
        materials = extract_feature(tower['nodes'], 'material')
        congruency = extract_feature(tower['nodes'], 'congruency')

        for ind in range(n_blocks):
            temp_tower = copy.copy(tower)
            blocks = temp_tower['nodes']
            temp_con = copy.copy(congruency)
            temp_con[ind] = False
            yield (ind, temp_tower)

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

    def movement(self, positions, eps = 1E-4):
        vel = (positions[-1] - positions[0]) / len(positions)
        return np.sum(np.abs(vel)) > eps

    #-------------------------------------------------------------------------#

    def __call__(self):
        """
        Evaluates the stability of the tower at each block.

        Returns:
          - The randomly sampled congruent tower.
          - The stability results for each block in the tower.
        """
        base_tower = self.sample_tower()
        d = {}
        for (block_id, tower) in self.configurations(base_tower):
            frames = self.simulate(tower)
            d.update({block_id : self.movement(frames)})

        return base_tower, d


# Helper functions

def extract_feature(blocks, feature):
    n_blocks = len(blocks)
    values = []
    for i in range(n_blocks):
        values.append(blocks['{0:d}'.format(i)[feature])
    return values

def apply_feature(blocks, feature, values):
    """
    Applys a feature to a set of blocks in a tower
    """
    n_blocks = len(blocks)
    n_values = len(values)
    if n_blocks != n_values:
        raise ValueError('Block, values missmatch')

    pprint.pprint(blocks)
    for b_i in n_blocks:
        block = blocks['{0:d]}'.format(b_i)]
        block[feature] = values[b_i]
    pprint.pprint(blocks)

    return blocks
