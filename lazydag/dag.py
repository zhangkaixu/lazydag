import dataclasses
from dataclasses import dataclass

#########################
# region: Hypergraph
from collections import defaultdict
class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret

@dataclass
class Vertex:
    graph: object
    name: str
    #successors: set = dataclasses.field(default_factory=set)
    #predecessors: set = dataclasses.field(default_factory=set)
    in_edges: list = dataclasses.field(default_factory=list)
    out_edges: list = dataclasses.field(default_factory=list)

    def __hash__(self):
        return hash(self.name)

    def _debug_links(self):
        print('name', self.name)
        #print('successors', *[v.name for v in self.successors])
        #print('predecessors', *[v.name for v in self.predecessors])

@dataclass
class Edge:
    #__slots__ = ('sources', 'targets')
    graph: object
    index: int
    sources: list # list of source vertices
    targets: list # list of target vertices

    def __post_init__(self):
        """
        (use `__post_init__` instead of `__init__` since this class is a dataclass)
        """
        for source in self.sources:
            self.graph._vertices[source].out_edges.append(self.index)
        for target in self.targets:
            self.graph._vertices[target].in_edges.append(self.index)
            #target.in_edges.append(self)

        #for source in self.predecessors:
        #    for target in self.successors:
        #        source.successors.add(target)
        #        target.predecessors.add(source)

    #@property
    #def successors(self):
    #    successors = set()
    #    for target in self.targets:
    #        successors.add(target)
    #        successors.update(target.successors)
    #    return successors

    #@property
    #def predecessors(self):
    #    predecessors = set()
    #    for source in self.sources:
    #        predecessors.add(source)
    #        predecessors.update(source.predecessors)
    #    return predecessors

class DAG:
    __slots__ = ('_vertices', '_edges')
    Vertex = Vertex
    Edge = Edge

    def __init__(self):
        self._vertices = keydefaultdict(lambda name: self.Vertex(self, name))
        self._edges = list()
    
    def add_edge(self, sources, targets):
        edge = self.Edge(self, len(self._edges), 
                         sources, 
                         targets,
                         )
        self._edges.append(edge)

# endregion

if __name__ == '__main__':
    dag = DAG()
    dag.add_edge(['a'], ['b'])
    dag.add_edge(['b'], ['c'])

    dag._vertices['a']._debug_links()
    dag._vertices['b']._debug_links()
    dag._vertices['c']._debug_links()

#