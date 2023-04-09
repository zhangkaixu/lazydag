import inspect
from collections import defaultdict
class Empty:
    pass
class LazyVariable:
    def __init__(self, name, value=Empty, func=Empty):
        self.name = name
        self._value = value
        self._func = func
        self._successors = set()
        self._predecessors = set()

    def _set_func(self, func):
        if self._func is not Empty:
            raise RuntimeError('func already set')
        self._func = func
    
    def _set_value(self, value):
        if self._func is not Empty:
            raise RuntimeError(
                f'can not set value to a var {self.name} whose func already set')
        self._value = value
        # make all sucessors `dirty`
        for successor in self._successors:
            successor._value = Empty
    
    def _set_returned_value(self, value):
        if self._value is not Empty:
            raise RuntimeError('value already set')
        self._value = value
    
    def _is_reachable(self):
        if self._value is not Empty:
            return True
        if self._func is Empty:
            return False
        return self._func._is_reachable()
    
    @property
    def value(self):
        if self._value is Empty:
            if self._func is Empty:
                raise AttributeError('value and func not set')
            self._func()
        if self._value is Empty:
            raise RuntimeError('value still not set after func call')
        return self._value

class LazyFunction:
    def __init__(self, return_values, func, *args, **kwargs):
        self.return_values = return_values
        self.func = func
        self.args = args
        self.kwargs = kwargs
        for value in self.return_values:
            value._set_func(self)
        
        all_predecessors = self._all_predecessors()
        all_successors = self._all_successors()
        #print('all_predecessors', [v.name for v in all_predecessors])
        #print('all_successors', [v.name for v in all_successors])

        # check for cycles
        inter = all_predecessors & all_successors
        if inter:
            names = [v.name for v in inter]
            raise RuntimeError('cycle detected for variables: ' + ', '.join(names))

        # propagate predecessors and successors
        for predecessor in all_predecessors:
            for successor in all_successors:
                predecessor._successors.add(successor)
                successor._predecessors.add(predecessor)

    
    def _all_predecessors(self):
        ret = set(self.args)
        ret |= set(self.kwargs.values())
        for arg in self.args:
            ret |= set(arg._predecessors)
        for value in self.kwargs.values():
            ret |= set(value._predecessors)
        return ret

    def _all_successors(self):
        ret = set(self.return_values)
        for value in self.return_values:
            ret |= set(value._successors)
        return ret

    def __call__(self):
        ret = self.func(*[value.value for value in self.args], 
                         **{k:v.value for k, v in self.kwargs.items()})
        if len(self.return_values) == 1:
            ret = [ret]
        for value, ret_value in zip(self.return_values, ret):
            value._set_returned_value(ret_value)
    
    def _is_reachable(self):
        return all(value._is_reachable() for value in self.args) and \
               all(value._is_reachable() for value in self.kwargs.values())


class LazyProperty(object):
    _NAME_PREFIX = '_'
    def __init__(self, func=Empty):
        self._func = func

    def __set_name__(self, owner, name):
        self.name = name
        self._name = self._NAME_PREFIX + name

    def _init_property(self, obj):
        name = self.name
        var = LazyVariable(name)
        setattr(obj, self._name, var)
        if self._func is not Empty:
            # parse the function signature
            import inspect
            fullargspec = inspect.getfullargspec(self._func)
            args = fullargspec.args

            # make sure the return value is not in the args
            if name in args:
                func_str = f'{self._func.__name__}{str(inspect.signature(self._func))}'
                raise RuntimeError(f'return value `{name}` in function {func_str} args')

            # make sure all args are initialized
            cls = type(obj)
            for arg in args:
                if not hasattr(obj, self._NAME_PREFIX + arg):
                    cls.__dict__[arg]._init_property(obj)

            # create a LazyFunction to calculate the value
            args = [getattr(obj, self._NAME_PREFIX + arg) for arg in args]
            LazyFunction([var], self._func, *args)

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self._name):
            self._init_property(obj)

        return getattr(obj, self._name).value

    def __set__(self, obj, value):
        if not hasattr(obj, self._name):
            self._init_property(obj)
        getattr(obj, self._name)._set_value(value)
    
    #def __delete__(self, obj):
    #    pass

lazy_property = LazyProperty


def lazyclass(cls):
    # add lazy properties
    lazy_properties = defaultdict(dict)
    for sup in list(reversed(cls.__mro__)):
        for key, func in sup.__dict__.items():
            if inspect.isfunction(func):
                fullargs = inspect.getfullargspec(func)
                if fullargs.args[0] == 'self':
                    continue
                else:
                    lazy_properties[key]['func'] = func
                    for arg in fullargs.args:
                        lazy_properties[arg]
            else:
                pass
            pass
    for k, v in lazy_properties.items():
        #print(k)
        if 'func' in v:
            p = LazyProperty(v['func'])
        else:
            p = LazyProperty()
        p.__set_name__(cls, k)
        setattr(cls, k, p)
    
    # add some methods
    def _set(self, **kwargs):
        """this method is only used to set lazy properties"""
        for k, v in kwargs.items():
            if ((k not in type(self).__dict__)
                or (not isinstance(type(self).__dict__[k], LazyProperty))):
                raise AttributeError(f'cannot set non-lazy property attribute {k} to {v}')
            setattr(self, k, v)
        return self
    setattr(cls, 'set', _set)

    def __init__(self, **kwargs):
        self.set(**kwargs)
    setattr(cls, '__init__', __init__)

    return cls