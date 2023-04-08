class LazyValue:
    class Empty:
        pass
    def __init__(self, value=Empty, func=Empty):
        self._value = value
        self._func = func
    
    def _set_func(self, func):
        if self._func is not self.Empty:
            raise RuntimeError('func already set')
        self._func = func
    
    def _set_value(self, value):
        if self._value is not self.Empty:
            raise RuntimeError('value already set')
        self._value = value
    
    def _is_reachable(self):
        if self._value is not self.Empty:
            return True
        if self._func is self.Empty:
            return False
        return self._func._is_reachable()
    
    @property
    def value(self):
        if self._value is self.Empty:
            if self._func is self.Empty:
                raise RuntimeError('value and func not set')
            self._func()
        if self._value is self.Empty:
            raise RuntimeError('value still not set after func call')
        return self._value

class LazyFunc:
    def __init__(self, return_values, func, *args, **kwargs):
        self.return_values = return_values
        self.func = func
        self.args = args
        self.kwargs = kwargs
        for value in self.return_values:
            value._set_func(self)
    def __call__(self):
        ret = self.func(*[value.value for value in self.args], 
                         **{k:v.value for k, v in self.kwargs.items()})
        if len(self.return_values) == 1:
            ret = [ret]
        for value, ret_value in zip(self.return_values, ret):
            value._set_value(ret_value)
    
    def _is_reachable(self):
        return all(value._is_reachable() for value in self.args) and \
               all(value._is_reachable() for value in self.kwargs.values())
