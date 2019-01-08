import copy
import json
import pprint

import numpy as np
import networkx as nx

from blockworld import blocks
from blockworld.towers.tower import Tower
from blockworld.utils.json_encoders import TowerEncoder

def load(json_file):

    if isinstance(json_file, str):
        with open(json_file, 'r') as f:
            d = json.load(f)
    else:
        d = json_file
    for block in d:
        data = block['data']
        if block['id'] == 0:
            c = blocks.BaseBlock(data['dims'][:2])
        else:
            c = blocks.SimpleBlock(data['dims'], data['pos'])
        block['data']['block'] = c
        del block['data']['pos']
        del block['data']['dims']

    g = nx.readwrite.json_graph.jit_graph(d, create_using=nx.DiGraph())
    return SimpleTower(g)

class SimpleTower(Tower):

    """
    Non-Empty instance of a `Tower`.


    Attributes:
        base_dimensions (tuple(float)): The dimensions of the base.
        blocks (`nx.Graph`(`Block`)): The graph describing the blocks composing
            the tower.
    """

    def __init__(self, blks):
        self.graph = blks

    # Properties #

    @property
    def base_dimensions(self):
        return self.base.dimensions

    @property
    def base(self):
        return self.blocks[0]['block']

    @property
    def blocks(self):
        return self.graph.nodes

    @property
    def ordered_blocks(self):
        keys = np.arange(1, len(self.blocks.keys()))
        return keys

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, blocks):

        if not isinstance(blocks, nx.DiGraph):
            msg = 'Type of given blocks is not valid.'
            raise ValueError(msg)

        if not 0 in blocks:
            msg = 'Tower does not have a base.'
            raise ValueError(msg)

        if len(blocks) <= 1:
            msg = 'When trying to initialize an empty tower use '+\
                  '`towers.EmptyTower`.'
            raise ValueError(msg)

        self._graph = blocks
        self.height = blocks

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, g):

        tops = [b for b in g if len(list(g.successors(b))) == 0]
        result = 0
        for top in tops:
            block = g.nodes[top]['block']
            result = max(block.mat[0,2], result)

        # used to adjust the total height
        base_height = self.base.mat[0,2]
        self._height = result - base_height

    # Methods #

    def __len__(self):
        return len(self.blocks) - 1

    def levels(self, block_ids = None):
        """
        Returns surface maps valid for block placement.
        """
        bs = self.blocks
        # get the top surface of each block
        if block_ids is None:
            block_ids = list(bs)

        blocks = [bs[b_id]['block'] for b_id in block_ids]

        zs = [b.mat[0,2] for b in blocks]
        layers = np.unique(zs)
        tz = list(zip(block_ids, blocks, zs))
        data = [(l, [(i,b) for i,b,z in tz if z == l]) for l in layers]
        return blocks, data

    def place_block(self, block, parents):
        """
        Returns a new tower with the given blocked added.
        """
        g = self.graph
        b_id = len(g)
        g.add_node(b_id, block = block)
        for parent in parents:
            g.add_edge(parent, b_id)
        new_tower = SimpleTower(g)
        return new_tower

    def get_stack(self, block_id):
        """
        Returns the parents of this block.
        """
        g = self.graph
        parents = list(nx.shortest_path(g, source = 0, target = block_id))
        return parents

    def is_stable(self):
        """
        Returns `True` for now.
        Not sure if method will remain.
        """
        return True

    def serialize(self, indent = None):
        """Return data in JIT JSON format.
        Parameters
        ----------
        G : NetworkX Graph
        indent: optional, default=None
            If indent is a non-negative integer, then JSON array elements and object
            members will be pretty-printed with that indent level. An indent level
            of 0, or negative, will only insert newlines. None (the default) selects
            the most compact representation.
        Returns
        -------
        data: JIT JSON string
        """
        json_graph = []
        for node in self.graph.nodes():
            json_node = {
                "id": node,
                "name": node
            }
            # node data
            d = {}
            attr = self.graph.nodes[node]
            for k in attr:
                if k == 'block':
                    d.update(attr[k].serialize())
                    # d[k] = self.graph.nodes[node][k].serialize()
                else:
                    d[k] = attr[k]
            json_node["data"] = d
            # adjacencies
            if self.graph[node]:
                json_node["adjacencies"] = []
                for neighbour in self.graph[node]:
                    adjacency = {
                        "nodeTo": neighbour,
                    }
                    # adjacency data
                    adjacency["data"] = self.graph.edges[node, neighbour]
                    json_node["adjacencies"].append(adjacency)
            json_graph.append(json_node)

        return json_graph


    def __repr__(self):
        return json.dumps(self.serialize())

    def apply_feature(self, feature, values):
        """
        Applys a feature to a set of blocks in a tower
        """
        n_blocks = len(self)
        n_values = len(values)
        if n_blocks != n_values:
            raise ValueError('Block, values missmatch')

        tower = copy.deepcopy(self)
        for b_id in np.arange(n_blocks):
            tower.blocks[b_id + 1][feature] = values[b_id]

        return tower

    def extract_feature(self, feature):
        """
        Retreives the given feature from each block in the tower.
        """
        n_blocks = len(self)
        values = []
        tower = copy.deepcopy(self)
        for b_id in np.arange(n_blocks) + 1:
            values.append(tower.blocks[b_id][feature])
        return np.array(values)
