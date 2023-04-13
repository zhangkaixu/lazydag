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
        

        @lazyclass
        class C:
            def a():
                return 3
            def b(a):
                return a * 2
        c = C()
        self.assertTrue(c.b==6)
    
    def test_subclass(self):
        from lazydag.lazyclass import lazyclass
        @lazyclass
        class A:
            def a(b):
                return b * 2
        @lazyclass
        class B(A):
            def b():
                return 3
        b = B()
        self.assertTrue(b.a==6)

        @lazyclass
        class A:
            def b():
                return 3
        @lazyclass
        class B(A):
            def a(b):
                return b * 2
        b = B()
        self.assertTrue(b.a==6)


        # test override
        @lazyclass
        class A:
            def a():
                return 'old'
            
            def b(a):
                return a * 2
        @lazyclass
        class B(A):
            def a():
                return 'new'
        b = B()
        self.assertTrue(b.a=='new')
        self.assertTrue(b.b=='newnew')

        # test assignment
        @lazyclass
        class A:
            def b(a):
                return a * 2
        @lazyclass
        class B(A):
            def c(b):
                return b + 1
        b = B()
        b.set(a=3)
    
    def test_default_value(self):
        from lazydag.lazyclass import lazyclass, LazyProperty
        @lazyclass
        class A:
            b: LazyProperty = 3
            c: "lazyproperty" = 4
            def a(b, c):
                return b + c
        
        a = A()
        self.assertTrue(a.a==7)

        a.set(b=4)
        self.assertTrue(a.a==8)

        print('00000000000000')
        @lazyclass
        class B(A):
            def d(b):
                return b * 2
            
        #print(B.__annotations__)
        b = B()
        self.assertTrue(b.d==6)

    def test_multiple_return(self):
        from lazydag.lazyclass import lazyclass

        @lazyclass
        class A:
            def c__b(a):
                return a+1, a-1
            def d(c):
                return c * 2
        a = A(a=3)
        self.assertTrue(a.c==4)
        self.assertTrue(a.b==2)
        a.set(a=4)
        self.assertTrue(a.d==10)

    def test_LazyClass(self):
        from lazydag.lazyclass import lazyclass

        @lazyclass
        class DAG:
            a: "lazy_property" = 4
            def sum(a, b):
                return a + b
            def double(sum):
                return sum * 2

        dag = DAG(b=3)
        self.assertTrue(dag.sum==7)     # `sum` was calculated in this line
        dag.set(a=5)                    # reset `a`
        self.assertTrue(dag.double==16) # `sum` was calculated again in this line

if __name__ == '__main__':
    unittest.main()