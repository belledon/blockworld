import copy
import pprint
import numpy as np

import blocks
import towers
import builders

class Generator:

    """
    Controls generation of towers.
    """

    stability_types = ['local', 'global']
    unknowns = ['H', 'L']

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
        Procedurally builds on top of the given `base` tower.
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
        materials = np.random.choice(self.materials,
                                     size = len(tower),
                                     p = self.mat_ps)

        tower = tower.apply_feature('substance', materials)
        tower = tower.apply_feature('appearance', materials)
        return tower

    def sample_tower(self):
        """
        Procedurally generates a tower.
        """
        tower = self.sample_structure()
        tower = self.sample_materials(tower)
        return tower


    def configurations(self, tower):
        """
        Generator for different tower configurations.

        Arguments:
            tower (`dict`) : Serialized tower structure.

        Returns:
            A generator with the i-th iteration representing the i-th
            block in the tower being replaced.

            Each iteration contains a dictionary of tuples corresponding
            to a tower with the replaced block having congruent or incongruent
            substance to its appearance, organized with respect to congruent
            material.

            { 'mat_i' : (congruent, incongruent)
              ...
        """
        subs = tower.extract_feature('substance')
        n_blocks = len(tower)
        for block_i in range(n_blocks):
            d = {}
            for mat_i in range(len(self.unknowns)):
                mt = copy.deepcopy(subs)
                mt[block_i] = self.unknowns[mat_i]
                base = tower.apply_feature('appearance', mt)
                cong_tower = base.apply_feature('substance', mt)

                mti = copy.deepcopy(subs)
                mti[block_i] = self.unknowns[(mat_i + 1) % len(self.unknowns)]
                inco_tower = base.apply_feature('substance', mti)

                d[self.unknowns[mat_i]] = (cong_tower, inco_tower)

            yield d


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
        for _ in range(n):
            base_tower = self.sample_tower()
            yield (base_tower, self.configurations(base_tower))


# Helper functions

# def extract_feature(blocks, feature):
#     n_blocks = len(blocks)
#     values = []
#     order = []
#     for block in blocks:
#         b_id = block['id']
#         if b_id > 0:
#             values.append(block[feature])
#             order.append(int(b_id) - 1)
#     return np.array(values)[order]

# def apply_feature(tower, feature, values):
#     """
#     Applys a feature to a set of blocks in a tower
#     """
#     tower = copy.deepcopy(tower)
#     n_blocks = len(tower)
#     n_values = len(values)
#     if n_blocks != n_values:
#         raise ValueError('Block, values missmatch')

#     for b_id, block in enumerate(tower.blocks):
#         if b_id == 0:
#             continue
#         block[feature] = values[b_id]

#     return tower
