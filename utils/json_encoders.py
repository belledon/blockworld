import json
import numpy as np
from pyquaternion import Quaternion

from blocks.simple_block import SimpleBlock

class TowerEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Quaternion):
            return list(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, SimpleBlock):
            return obj.serialize()
        return json.JSONEncoder.default(self, obj)
