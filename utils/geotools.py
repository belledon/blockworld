import numpy as np
from shapely import geometry, affinity


def make_grid(block, step = 0.1):
    bbox = block.surface.bounds
    xs = np.arange(bbox[0], bbox[2] + step, step)
    ys = np.arange(bbox[1], bbox[3] + step, step)
    grid = np.array(np.meshgrid(xs, ys)).T.reshape(-1, 2)
    grid = np.round(grid, 2)
    return geometry.MultiPoint(grid)

def propose_placements(block, grid, z):
    """
    Returns a mapping of a block to each point in the grid.
    """
    f = lambda point : block.moveto(point, z)
    return list(map(f, grid))


def local_stability(block, layer):
    """
    Returns `True` if the `block` is positioned in such a way as to
    satisfy local stability (see repo for more info).
    """
    f = lambda s: block.surface.intersects(s)
    touching = list(filter(f, layer))
    if len(touching) == 0:
        return False
    elif len(touching) == 1:
        return touching[0].contains(block.com)
    else:
        r = geometry.MultiPolygon(touching).envelope
        return r.contains(block.com)
