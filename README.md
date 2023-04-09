# lazydag
A Directed Acyclic Graph for lazy evaluation for Python

```python
from lazydag.lazyclass import lazyclass

@lazyclass
class DAG:
    def sum(a, b):
        return a + b
    def double(sum):
        return sum * 2

dag = DAG(a=4, b=3)
self.assertTrue(dag.sum==7)     # `sum` was calculated in this line
dag.set(a=5)                    # reset `a`
self.assertTrue(dag.double==16) # `sum` was calculated again in this line
```
