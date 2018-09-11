
import numpy as np

from . import substances

class Material:

    def __init__(self, name):
        self.name = name


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, s):
        if not isinstance(s, str):
            raise ValueError('Name must be string.')

        if s in substances.density and s in substances.friction:
            self.density = substances.density[s]
            self.friction = substances.friction[s]
        else:
            # unknown
            self.density = np.random.uniform(1.0, 10.0)
            self.friction = np.random.uniform(0.1, 0.9)

    def seraliaze(self):
        return {'density' : self.density, 'friction' : self.friction}
