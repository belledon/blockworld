import numpy as np
import pybullet as p
# import pybullet_data

class Loader:

    """
    Interface for loading object data.
    """

    def __call__(self, name, start):

        if name == '0':
            mesh = p.GEOM_CYLINDER
            col_id = p.createCollisionShape(mesh, radius = 40)
            rot = p.getQuaternionFromEuler(start['rot'])
            mass = 0
        else:
            mesh = p.GEOM_BOX
            col_id = p.createCollisionShape(mesh,
                                            halfExtents = start['dimensions'])
            mass = np.prod(start['dimensions']) * start['density']
            rot = p.getQuaternionFromEuler(start['rot'])

        obj_id = p.createMultiBody(baseMass = 0,
                                   baseCollisionShapeIndex = col_id,
                                   basePosition = [0,0,0],
                                   baseOrientation = rot)

        return obj_id

class TowerPhysics:

    """
    Handles physics for block towers.
    """

    def __init__(self, description, loaders):
        self.physicsClient = p.connect(p.DIRECT)
        # p.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally
        p.setGravity(0,0,-10)
        self.loader = loader
        self.description = description

    #-------------------------------------------------------------------------#
    # Attributes

    @property
    def loader(self):
        return self._loader

    @loader.setter
    def loader(self, l):
        if not isinstance(l, Loader):
            raise TypeError('Loader has wrong type')


    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, w):
        if not isinstance(w, dict):
            raise TypeError('World description must be a `dict`.')
        block_d = {}
        for block_key in w:
            start = w[block_key]
            block_id = self.loaders(block_key, start)
            block_d[block_key] = block_id

        self._world = block_d

    #-------------------------------------------------------------------------#
    # Methods

    def trace(self, frames, objects):
        """
        Obtains world state for select frames.
        Currently returns the position of each rigid body.
        """
        positions = np.array((len(frames), len(objects), 3))
        rotations = np.array((len(frames), len(objects), 3))

        for c, obj in enumerate(objects):
            if not obj in self.word.keys():
                raise ValueError('Block {} not found'.format(obj))

            for f range(frames):
                p.stepSimulation()
                pos, rot = p.getBasePositionAndOrientation(obj)
                positions[f,c] = pos
                rotations[f,c] = p.getEulerFromQuaternion(rot)

        return {'positions' : positions, 'rotations' : rotations}
