import numpy as np
import pybullet as p

class Loader:

    """
    Interface for loading object data.
    """

    def __call__(self, name, start, p_id):

        rot = p.getQuaternionFromEuler([0, 0, 0])
        if name == 0:
            mesh = p.GEOM_PLANE
            col_id = p.createCollisionShape(mesh, physicsClientId = p_id)
            pos = [0,0,0]
            mass = 0
            friction = 0.5
        else:
            mesh = p.GEOM_BOX
            dims = np.array(start['dims']) / 2.0
            col_id = p.createCollisionShape(mesh,
                                            halfExtents = dims,
                                            physicsClientId = p_id
                                            )
            pos = start['pos']
            mass = np.prod(start['dims']) * start['substance']['density']
            friction = start['substance']['friction']

        obj_id = p.createMultiBody(mass, col_id, -1, pos, rot,
                                   physicsClientId = p_id)
        p.changeDynamics(obj_id, -1, lateralFriction = friction,
                         physicsClientId = p_id)

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
        p_id = self.physicsClient
        block_d = {}
        for block in w:
            start = block['data']
            block_key = block['id']
            block_id = self.loader(block_key, start, p_id)
            block_d[block_key] = block_id

        self._world = block_d

    #-------------------------------------------------------------------------#
    # Methods

    def __enter__(self):
        self.physicsClient = p.connect(p.DIRECT)
        p.resetSimulation()
        self.world = self.description
        return self

    def __exit__(self, *args):
        p.disconnect(self.physicsClient)

    def get_trace(self, frames, objects, time_step = 120, fps = 60):
        """
        Obtains world state for select frames.
        Currently returns the position of each rigid body.
        """
        for obj in objects:
            if not obj in self.world.keys():
                raise ValueError('Block {} not found'.format(obj))

        p_id = self.physicsClient
        p.setGravity(0,0,-10, physicsClientId = p_id)
        p.setPhysicsEngineParameter(
            fixedTimeStep = 1.0 / time_step,
            numSolverIterations = 200,
            enableConeFriction = 0,
            physicsClientId = p_id
        )

        positions = np.zeros((frames, len(objects), 3))
        rotations = np.zeros((frames, len(objects), 4))

        phys_step_per_frame = time_step / fps
        dur = int(phys_step_per_frame * frames)
        for f in range(dur):
            p.stepSimulation(physicsClientId = p_id)

            if f % phys_step_per_frame != 0:
                continue
            for c, obj in enumerate(objects):
                obj_id = self.world[obj]
                pos, rot = p.getBasePositionAndOrientation(obj_id, physicsClientId = p_id)
                frame = int(f / phys_step_per_frame)
                positions[frame, c] = np.asarray(pos).flatten()
                rotations[frame, c] = np.asarray(rot).flatten()

        result = {'position' : positions, 'rotation' : rotations}
        return result


    #-------------------------------------------------------------------------#
    # Helpers
