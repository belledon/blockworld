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

    def __init__(self, tower_json, loader = Loader()):
        self.loader = loader
        self.description = tower_json
        p = bc.BulletClient(connection_mode=pybullet.DIRECT)
        p.resetSimulation()
        self.physicsClient = p

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
        p = self.physicsClient
        block_d = {}
        for block in w:
            start = block['data']
            block_key = block['id']
            block_id = self.loader(block_key, start, p)
            block_d[block_key] = block_id

        self._world = block_d

    #-------------------------------------------------------------------------#
    # Methods

    def __enter__(self):
        # p = bc.BulletClient(connection_mode=pybullet.DIRECT)
        # self.physicsClient.resetSimulation()
        # self.physicsClient = p
        self.world = self.description
        return self

    def __exit__(self, *args):
        # del self.physicsClient
        # self.physicsClient = None
        self.physicsClient.resetSimulation()

    def get_trace(self, frames, objects, time_step = 120, fps = 60):
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

        p = self.physicsClient
        p.setGravity(0,0,-10)
        p.setPhysicsEngineParameter(
            fixedTimeStep = 1.0 / time_step,
            numSolverIterations = 100,
            enableConeFriction = 0,
        )

        positions = np.zeros((frames, len(objects), 3))
        rotations = np.zeros((frames, len(objects), 4))

        steps_per_frame = int(time_step / fps)
        dur = int(max(1, ((frames / fps) * time_step)))
        for f in range(dur):
            p.stepSimulation()

            if f % steps_per_frame != 0:
                continue
            for c, obj in enumerate(objects):
                obj_id = self.world[obj]
                pos, rot = p.getBasePositionAndOrientation(obj_id)
                frame = int(f / steps_per_frame)
                positions[frame, c] = np.array(pos).flatten()
                rotations[frame, c] = np.array(rot).flatten()

        result = {'position' : positions, 'rotation' : rotations}
        return result
