# lazydag
A Directed Acyclic Graph for lazy evaluation for Python

```python
from lazydag import LazyDAG
dag = LazyDAG(a=3)
dag.add_edge(['c'], lambda a, b:a+b, 'a', 'b')

@dag.edge
def d(a, b):
    return a*b

self.assertEqual(dag(b=4).c, 7)
self.assertEqual(dag(b=9).c, 12)
self.assertEqual(dag(b=3).d, 9)
```
