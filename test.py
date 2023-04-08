import unittest

class TestLazy(unittest.TestCase):
    def test_lazy(self):
        from lazydag.lazy import LazyFunc, LazyValue
        a = LazyValue(3)
        b = LazyValue()
        c = LazyValue()
        self.assertFalse(c._is_reachable())
        LazyFunc([c], lambda a, b: a+b, a, b)
        b._set_value(4)
        self.assertTrue(c._is_reachable())
        self.assertEqual(c.value, 7)

class TestLazyDAG(unittest.TestCase):
    def test_LazyDAG(self):
        from lazydag import LazyDAG
        dag = LazyDAG(a=3)
        dag.add_edge(['c'], lambda a, b:a+b, 'a', 'b')

        @dag.edge
        def d(a, b):
            return a*b

        self.assertEqual(dag(b=4).c, 7)
        self.assertEqual(dag(b=9).c, 12)
        self.assertEqual(dag(b=3).d, 9)

#class TestStringMethods(unittest.TestCase):
#    def test_upper(self):
#        self.assertEqual('foo'.upper(), 'FOO')
#
#    def test_isupper(self):
#        self.assertTrue('FOO'.isupper())
#        self.assertFalse('Foo'.isupper())
#
#    def test_split(self):
#        s = 'hello world'
#        self.assertEqual(s.split(), ['hello', 'world'])
#        # check that s.split fails when the separator is not a string
#        with self.assertRaises(TypeError):
#            s.split(2)

if __name__ == '__main__':
    unittest.main()
