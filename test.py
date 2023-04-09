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

class TestLazyClass(unittest.TestCase):
    def test_LazyProperty(self):
        from lazydag.lazyclass import LazyProperty

        class A:
            a = LazyProperty()
            b = LazyProperty()

            @LazyProperty
            def c(a, b):
                return a+b
        
        a = A()
        a.a = 4
        a.b = 3
        self.assertEqual(a.c, 7)
        a.a = 5
        self.assertEqual(a.c, 8)

    def test_LazyClass_bad_dag(self):
        from lazydag.lazyclass import lazyclass

        # self reference
        with self.assertRaises(RuntimeError):
            @lazyclass
            class A:
                def a(a, b):
                    return a * 2
            a = A()
            a.set(b=3)
            a.a

        # cycle
        with self.assertRaises(RuntimeError):
            @lazyclass
            class A:
                def b(a):
                    return a * 2
                def c(b, d):
                    return 2
                def d(c):
                    return 3
            a = A()
            a.set(a=3)
            a.d

    def test_LazyClass_chain(self):
        from lazydag.lazyclass import lazyclass
        @lazyclass
        class A:
            def b(a):
                return a * 2
            def c(b):
                return 2 + b
        a = A()
        a.set(a=3)
        self.assertTrue(a.c==8)

    def test_LazyClass_set(self):
        from lazydag.lazyclass import lazyclass
        @lazyclass
        class A:
            def sum(a, b):
                return a + b
        
        a = A()
        with self.assertRaises(AttributeError):
            a.set(e=45) # can not set attribute `e`
        with self.assertRaises(AttributeError):
            a.a         # 💥 attribute not set

        @lazyclass
        class A:
            def a(b):
                return b * 2
        # set a function
        with self.assertRaises(RuntimeError):
            a = A()
            a.set(a=3)

    def test_LazyClass(self):
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

if __name__ == '__main__':
    unittest.main()