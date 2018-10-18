import numpy as np
import pybullet as p

class Loader:

    """
    Interface for loading object data.
    """

    def __call__(self, name, start):

        rot = p.getQuaternionFromEuler([0, 0, 0])
        if name == 0:
            mesh = p.GEOM_CYLINDER
            col_id = p.createCollisionShape(mesh, radius = 40,
                                            # physClientId = pid
            )
            pos = [0,0,0]
            mass = 0
            friction = 0.5
        else:
            mesh = p.GEOM_BOX
            dims = np.array(start['dims']) / 2.0
            col_id = p.createCollisionShape(mesh,
                                            halfExtents = dims,
                                            # physClientId = pid)
                                            )
            pos = start['pos']
            mass = np.prod(start['dims']) * start['substance']['density']
            friction = start['substance']['friction']

        obj_id = p.createMultiBody(baseMass = 0,
                                   baseCollisionShapeIndex = col_id,
                                   basePosition = pos,
                                   baseOrientation = rot,
                                   # physClientId = pid,
        )

        p.changeDynamics(obj_id, -1, mass = mass, lateralFriction = friction)

        return obj_id

class TowerPhysics:

    """
    Handles physics for block towers.
    """

    def __init__(self, tower_json, loader = Loader()):
        self.loader = loader
        self.description = tower_json

    #-------------------------------------------------------------------------#
    # Attributes

    @property
    def loader(self):
        return self._loader

    @loader.setter
    def loader(self, l):
        if not isinstance(l, Loader):
            raise TypeError('Loader has wrong type')
        self._loader = l


    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, w):
        block_d = {}
        for block in w:
            start = block['data']
            block_key = block['id']
            block_id = self.loader(block_key, start)
            block_d[block_key] = block_id

        self._world = block_d

    #-------------------------------------------------------------------------#
    # Methods

    def __enter__(self):
        # p = p
        self.physicsClient = p.connect(p.DIRECT)
        self.world = self.description
        return self

    def __exit__(self, *args):
        p.disconnect()
        print('closed pybullet')

    def get_trace(self, frames, objects):
        """
        Obtains world state for select frames.
        Currently returns the position of each rigid body.
        """
        results = []
        p.setGravity(0,0,-10)
        time_step = 100 # number of steps per second
        p.setPhysicsEngineParameter(
            fixedTimeStep = 1.0 / time_step,
            numSolverIterations = 200,
        )

        positions = np.zeros((frames, len(objects), 3))
        rotations = np.zeros((frames, len(objects), 4))
        for f in range(frames * time_step):
            p.stepSimulation()

            if f % time_step != 0:
                continue
            for c, obj in enumerate(objects):
                # if not obj in self.world.keys():
                #     raise ValueError('Block {} not found'.format(obj))
                pos, rot = p.getBasePositionAndOrientation(obj)
                frame = int(f / time_step)
                positions[frame, c] = np.asarray(pos).flatten()
                rotations[frame, c] = np.asarray(rot).flatten()

        result = {'position' : positions, 'rotation' : rotations}
        print(result['position'])
        return result


    #-------------------------------------------------------------------------#
    # Helpers
