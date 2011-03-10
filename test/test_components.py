import unittest
from components import *

class Test(unittest.TestCase):
    def test_zone_component_decorator(self):
        @zone_component(author="A")
        class TestComponent:
            pass
        component_info = TestComponent.component_info

        # test author
        self.assertEqual(component_info['author'], "A")
        self.assertTrue(component_info['zone'])
    
    def test_function_decorator_unchained(self):
        @zone_component()
        class TestComponent:
            @function_decorator('test', 1, False)
            def my_function(self):
                pass
        component_info = TestComponent.component_info
        self.assertEqual(component_info['ext_func']['test'][0][1], 1)
    
    def test_function_decorator_chained(self):
        @zone_component()
        class TestComponent:
            @function_decorator('test', 1, True)
            @function_decorator('test', 2, True)
            def my_function(self):
                pass
        component_info = TestComponent.component_info
        self.assertEqual(sorted(component_info['ext_func']['test'][0][1]), [1, 2])

    def test_duplicate_function_decorator(self):
        @zone_component()
        class TestComponent:
            @function_decorator('test', 1, False)
            def foo(self):
                pass
            @function_decorator('test', 2, False)
            def bar(self):
                pass
        component_info = TestComponent.component_info
        values = [v for func, v in component_info['ext_func']['test']]
        self.assertEqual(sorted(values), [1, 2])

    def test_component_decorator_unchained(self):
        @zone_component()
        @component_decorator('test', 1, False)
        class TestComponent:
            pass
        component_info = TestComponent.component_info
        self.assertEqual(component_info['ext_comp']['test'], 1)
    
    def test_component_decorator_chained(self):
        @zone_component()
        @component_decorator('test', 1, True)
        @component_decorator('test', 2, True)
        class TestComponent:
            pass
        component_info = TestComponent.component_info
        self.assertEqual(sorted(component_info['ext_comp']['test']), [1, 2])

    def test_uses_zone_interface(self):
        @zone_component()
        @uses_zone_interface('a')
        @uses_zone_interface('b', 'c')
        class TestComponent:
            def __init__(self):
                self.initialized = True
        component = TestComponent(a=1, b=2)
        self.assertEqual(component.a, 1)
        self.assertEqual(component.c, 2)
        self.assertTrue(component.initialized)

if __name__ == "__main__":
    unittest.main()