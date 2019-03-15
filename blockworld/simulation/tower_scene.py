import numpy as np
import pybullet
import pybullet_utils.bullet_client as bc

class Loader:

    """
    Interface for loading object data.
    """

    def __call__(self, name, start, p):

        rot = p.getQuaternionFromEuler([0, 0, 0])
        if name == 0:
            mesh = p.GEOM_PLANE
            col_id = p.createCollisionShape(mesh)
            pos = [0,0,0]
            mass = 0
            friction = 0.5
        else:
            mesh = p.GEOM_BOX
            dims = np.array(start['dims']) / 2.0
            col_id = p.createCollisionShape(mesh,
                                            halfExtents = dims,
                                            )
            pos = start['pos']
            mass = np.prod(start['dims']) * start['substance']['density']
            friction = start['substance']['friction']

        obj_id = p.createMultiBody(mass, col_id, -1, pos, rot)
        p.changeDynamics(obj_id, -1, lateralFriction = friction)
        return obj_id

class TowerPhysics:

    """
    Handles physics for block towers.
    """

    def __init__(self, tower_json, loader = None):
        if loader is None:
            loader = Loader()
        self.loader = loader
        self.client = bc.BulletClient(connection_mode=pybullet.DIRECT)
        self.world = tower_json

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
        self.client.resetSimulation()
        block_d = {}
        for block in w:
            start = block['data']
            block_key = block['id']
            block_id = self.loader(block_key, start, self.client)
            block_d[block_key] = block_id

        self._world = block_d

    #-------------------------------------------------------------------------#
    # Methods

    def get_trace(self, frames, objects, time_step = 240, fps = 60):
        """Obtains world state from simulation.

        Currently returns the position of each rigid body.
        The total duration is equal to `frames / fps`

        Arguments:
            frames (int): Number of frames to simulate.
            objects ([str]): List of strings of objects to report
            time_step (int, optional): Number of physics steps per second
            fps (int, optional): Number of frames to report per second.
        """
        for obj in objects:
            if not obj in self.world.keys():
                raise ValueError('Block {} not found'.format(obj))
        object_ids = [self.world[obj] for obj in objects]

        p = self.client
        p.setPhysicsEngineParameter(
            # useSplitImpulse = 1,
            # splitImpulsePenetrationThreshold = 0.9
            fixedTimeStep = 1.0 / time_step,
            # numSolverIterations = 100,
            enableConeFriction = 0,
            # contactERP = 0.2

        )
        p.setGravity(0, 0, -10)

        positions = np.zeros((frames, len(objects), 3))
        rotations = np.zeros((frames, len(objects), 4))

        steps_per_frame = int(time_step / fps)
        total_steps = int(max(1, ((frames / fps) * time_step)))
        for step in range(total_steps):
            p.stepSimulation()

            if step % steps_per_frame != 0:
                continue

            for c, obj_id in enumerate(object_ids):
                pos, rot = p.getBasePositionAndOrientation(obj_id)
                frame = np.floor(step / steps_per_frame).astype(int)
                positions[frame, c] = pos
                rotations[frame, c] = rot

        result = {'position' : positions, 'rotation' : rotations}
        return result
