import unittest
import compman
from components import zone_component

class Test(unittest.TestCase):
    def setUp(self):
        self.component_manager = compman.ComponentManager()

    def test_loaders(self):
        class TestLoader:
            def __init__(self):
                self.called = False
        
            def get_component_class(self, component_name):
                @zone_component()
                class TestClass:
                    pass
                self.called = True
                self.component_name = component_name
                return TestClass

        # setup the loader and add it
        my_loader = TestLoader()
        self.component_manager.add_loader(my_loader, "<test>")
        self.assertIn(("<test>",my_loader), self.component_manager.loaders.items())
        
        # test that the loader gets called properly
        self.component_manager.load_list(["<test> component"], None)
        self.assertTrue(my_loader.called)
        self.assertEqual(my_loader.component_name, "component")

        # remove the loader
        self.component_manager.remove_loader(my_loader, "<test>")
        self.assertNotIn(("<test>",my_loader), self.component_manager.loaders.items())

    def test_graph_resolver(self):
        # TODO: do this
        pass
    
    def test_interface_creation(self):
        # TODO: do this
        pass

if __name__ == "__main__":
    unittest.main()