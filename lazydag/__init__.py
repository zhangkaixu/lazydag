import dataclasses
from dataclasses import dataclass

from .dag import DAG, Vertex, Edge
from .lazy import LazyValue, LazyFunc

@dataclass
class LazyVertex(Vertex):
    value: LazyValue = dataclasses.field(default_factory=LazyValue)

    def _set_value(self, value=LazyValue.Empty):
        self.value = LazyValue(value)
        if value is not LazyValue.Empty:
            self._update()

    def _update(self):
        for edge in self.out_edges:
            self.graph._edges[edge]._update()
            #edge._update()
    
    def _is_reachable(self):
        return self.value._is_reachable()

    def __hash__(self):
        return hash(self.name)

class FuncWrapper:
    def __init__(self, return_values, func, *args, **kwargs):
        self.return_values = return_values
        self.func = func
        self.args = args
        self.kwargs = kwargs

@dataclass
class LazyEdge(Edge):
    func_wrapper : FuncWrapper = None
    function: LazyFunc = None
    def _update(self):
        if self.function is not None:
            return
        # check if all sources are reachable
        for source in self.sources:
            source = self.graph._vertices[source]
            if not source._is_reachable():
                return

        # check if all targets are not reachable
        for target in self.targets:
            target = self.graph._vertices[target]
            if target._is_reachable():
                raise RuntimeError(f'target {target} is already reachable')

        # when all sources are reachable and all targets are not reachable
        # create the function
        for vertex in self.func_wrapper.return_values:
            # set new values for targets
            vertex = self.graph._vertices[vertex]
            vertex._set_value()
        return_values = [self.graph._vertices[vertex].value for vertex in self.func_wrapper.return_values]
        args = [self.graph._vertices[vertex].value for vertex in self.func_wrapper.args]
        kwargs = {k:self.graph._vertices[vertex].value for k, vertex in self.func_wrapper.kwargs.items()}
        #args = [vertex.value for vertex in self.func_wrapper.args]
        #kwargs = {k:vertex.value for k, vertex in self.func_wrapper.kwargs.items()}
        self.function = LazyFunc(return_values, 
                                 self.func_wrapper.func, 
                                 *args, 
                                 **kwargs)
        # update targets
        for target in self.targets:
            target = self.graph._vertices[target]
            target._update()
        pass

class LazyDAG(DAG):
    Vertex = LazyVertex
    Edge = LazyEdge

    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            self._set_value(k, v)
    
    def _copy(self):
        other = type(self)()
        other._vertices = {k:dataclasses.replace(v, graph=other) for k, v in self._vertices.items()}
        other._edges = [dataclasses.replace(e, graph=other) for e in self._edges]
        return other
    
    def add_edge(self, targets, func, *args, **kwargs):
        # add edge to DAG
        sources = list(args) + list(kwargs.values())
        super().add_edge(sources, targets)
        self._edges[-1].func_wrapper = FuncWrapper(targets, func, *args, **kwargs)
    
    def edge(self, func):
        import inspect
        fullargs = inspect.getfullargspec(func)

        args = fullargs.args
        targets = [func.__name__]
        self.add_edge(targets, func, *args)


    def __call__(self, **kwargs):
        other = self._copy()
        for k, v in kwargs.items():
            other._set_value(k, v)
        return other

    def _is_reachable(self, name):
        return self._vertices[name]._is_reachable()
    
    def _set_value(self, name, value):
        self._vertices[name]._set_value(value)
    
    def _get_value(self, name):
        if self._vertices[name].value._is_reachable():
            return self._vertices[name].value.value
    
    #def __getitem__(self, name):
    #    if isinstance(name, int):
    #        return self._edges[name]
    #    else:
    #        return self._get_value(name)
    
    def __getattr__(self, name):
        return self._get_value(name)
    
if __name__ == '__main__':
    pass