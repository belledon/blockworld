
import numpy as np

"""
Values used throughout simulation
"""

density = {
    'Wood' : 3.0,
    'Metal' : 7.0,
    'H' : 9.0,
    'L' : 1.0
}

friction = {
    'Wood' : 0.5,
    'Metal' : 0.2,
    'H' : 0.5,
    'L' : 0.5
}

class Substance:

    """
    Manages physical property assignment.

    If the `name` is known, then assignment is
    deterministic as defined by `substances.friction`
    and `substances.density`.

    If the substance is not known, then a `density` and
    `friction` pair is independently sampled from
    Uniform distributions.

    Attributes:

      - name (str): String identifier.
      - density (float): Density sample.
      - friction (float): Friction sample.

    Methods:
      - serialize (self): Returns a `dict` containing
        the physical properties.
    """

    def __init__(self, name):
        self.name = name


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, s):
        if not isinstance(s, str):
            raise ValueError('Name must be string.')

        if s in density and s in friction:
            self.density = density[s]
            self.friction = friction[s]
        else:
            # unknown
            self.density = np.random.uniform(1.0, 10.0)
            self.friction = np.random.uniform(0.1, 0.9)

    def serialize(self):
        return {'density' : float(self.density),
                'friction' : float(self.friction)}
