

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


    def configurations(self):
        """
        Generator for different tower configurations.
        """
        tower = self.structure
        n_blocks = len(tower['nodes']) - 1

        for ind in range(n_blocks):

            temp_tower = copy.copy(tower)
            blocks = temp_tower['nodes']
            materials = np.random.choice([1, 0],
                                         size = n_blocks,
                                         p = self.mat_ps)

            for b_i, block in enumerate(blocks):
                material = materials[b_i]
                block['material'] = material
                if int(block['id']) == (ind + 1):
                    block['appearance'] = self.materials[1 - orig_material]

                else:
                    block['appearance'] = self.materials[materials[b_i]]

            yield (ind, temp_tower)

    def simulate(self, tower):
        """
        Controls simulations and extracts positions
        """
        scene = BlockScene(tower, frames = 10)
        scene.bake_physics()
        trace = scene.get_trace(frames = [0, 10])
        return [t['position'] for t in trace]

    def movement(self, positions, eps = 1E-4):
        vel = (positions[-1] - positions[0]) / len(positions)
        return np.sum(np.abs(vel)) > eps

    def __call__(self):
        """
        Evaluates the stability of the tower at each block.
        """
        d = {}
        for (block_id, tower) in self.configurations():
            frames = self.simulate(tower)
            d.update({block_id : self.movement(frames)})

        return d
