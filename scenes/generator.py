import copy
import pprint
import numpy as np

import blocks
import towers
import builders

class Generator:

    """
    Controls generation of towers
    """
    stability_types = ['local', 'global']
    def __init__(self, base, n_blocks, materials, stability):
        self.base = base
        self.n_blocks = n_blocks
        self.materials = materials
        self.builder = stability

    # Properties and Setters

    @property
    def n_blocks(self):
        return self._n_blocks

    @n_blocks.setter
    def n_blocks(self, n):
        n = int(n)
        if n <= 0 :
            raise ValueError('n_blocks must be > 1.')
        self._n_blocks = n

    @property
    def materials(self):
        return self._materials

    @materials.setter
    def materials(self, m):
        keys, vals = zip(*m.items())
        if np.sum(vals) != 1:
            raise ValueError('Material distribution does not sum to one.')
        else:
            self._materials = list(keys)
            self._mat_ps = list(vals)

    @property
    def mat_ps(self):
        return self._mat_ps

    @property
    def builder(self):
        return self._builder

    @builder.setter
    def builder(self, s):
        if (not isinstance(s, str)) or \
           (not s in self.stability_types):
            raise ValueError('Unkown builder type.')

        self._builder = builders.SimpleBuilder(self.n_blocks)

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, b):
        if isinstance(b, towers.tower.Tower):
            self._base = b
        else:
            try:
                b = list(b)
            except:
                raise ValueError('Unsupported base.')
            self._base = towers.EmptyTower(b)


    #-------------------------------------------------------------------------#

    # Material assignment and sampling

    def sample_blocks(self):
        """
        Procedurally generates blocks of cardinal orientations.
        """
        for i in range(self.n_blocks):
            block_dims = np.array([2, 1, 1])
            np.random.shuffle(block_dims)
            yield blocks.SimpleBlock(block_dims)

    def sample_structure(self):
        """
        Procedurally builds on top of a `base` structure.
        """
        base = copy.copy(self.base)
        blocks = self.sample_blocks()
        new_tower = self.builder(base, blocks)
        return new_tower

    def sample_materials(self, tower):
        """
        Procedurally assigns substance and appearance to each block
        in a tower structure.
        """
        tower = copy.deepcopy(tower)
        blocks = tower['nodes']
        materials = np.random.choice(self.materials,
                                     size = self.n_blocks,
                                     p = self.mat_ps)

        blocks = apply_feature(blocks, 'substance', materials)
        blocks = apply_feature(blocks, 'appearance', materials)
        tower['nodes'] = blocks
        return tower

    def sample_tower(self):
        """
        Procedurally generates a tower.
        """
        struct = self.sample_structure().serialize()
        tower = self.sample_materials(struct)
        return tower


    def configurations(self, tower):
        """
        Generator for different tower configurations.
        """
        materials = extract_feature(tower['nodes'], 'material')
        congruency = extract_feature(tower['nodes'], 'congruency')

        for ind in range(self.n_blocks):
            temp_tower = copy.copy(tower)
            blocks = temp_tower['nodes']
            temp_con = copy.copy(congruency)
            temp_con[ind] = False
            yield (ind, temp_tower)

    #-------------------------------------------------------------------------#

    def __call__(self, n = 1):
        """
        Generates the given number of random towers.

        Arguments:
          - n (optional) : The number of towers to generate.
        Returns:
          A generator yielding tuples of the for (tower, configurations).
          - tower (`Tower`) : The randomly sampled congruent tower.
          - configurations : A generator over incongruency for each block.
        """
        for i in range(n):
            base_tower = self.sample_tower()
            yield (base_tower, self.configurations(base_tower))


# Helper functions

def extract_feature(blocks, feature):
    n_blocks = len(blocks)
    values = []
    order = []
    for block in blocks:
        b_id = block['id']
        if b_id > 0:
            values.append(block[feature])
            order.append(int(b_id) - 1)
    return np.array(values)[order]

def apply_feature(blocks, feature, values):
    """
    Applys a feature to a set of blocks in a tower
    """
    n_blocks = len(blocks) - 1
    n_values = len(values)
    if n_blocks != n_values:
        raise ValueError('Block, values missmatch')

    for block in blocks:
        b_id = block['id']
        if b_id > 0:
            block[feature] = values[int(b_id) - 1]

    return blocks
