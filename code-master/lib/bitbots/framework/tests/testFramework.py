#-*- coding:utf-8 -*-
import unittest

from bitbots.framework import Runtime
from bitbots.debug import Scope


class TestFramework(unittest.TestCase):
    
       
    @classmethod
    def setUpClass(cls):   
        print "#### Test Framework ####"
    
    def test_module_loading_and_resolving(self):
        # Top Level is here tests
        IMPORTS = ["bitbots.framework.tests.dummy_module", "bitbots.framework.tests.dummy_module2"]
        debug = Scope("Testing")
        
        # Module laden
        runtime = Runtime(debug)
        for name in IMPORTS:
            runtime.load(name)
        
        self.assertIn("DummyModule", runtime.service.modules, str(runtime.service.modules))
        self.assertIn("A", runtime.service.modules["DummyModule"].provides)
        self.assertIn("B", runtime.service.modules["DummyModule"].provides)
        
        self.assertIn("DummyModule2", runtime.service.modules)
        self.assertIn("A", runtime.service.modules["DummyModule2"].requires)
        self.assertIn("B", runtime.service.modules["DummyModule2"].requires)
        self.assertIn("C", runtime.service.modules["DummyModule2"].provides)

        
        # Just call Resolve with DummyModule2 - It should then automatically load DummyModule too
        result = runtime.service.resolve(["DummyModule2"])
        self.assertEquals("DummyModule", result[0])
        self.assertEquals("DummyModule2", result[1])
        
    @unittest.expectedFailure
    def test_no_provider(self):
        # Top Level is here tests
        IMPORTS = ["tests.DummyModule", "tests.DummyModule2"]
        debug = Scope("Testing")
        
         # Module laden
        runtime = Runtime(debug)
        for name in IMPORTS:
            runtime.load(name)
        
        self.assertTrue("DummyModule" in runtime.service.modules)
        self.assertTrue("DummyModule2" in runtime.service.modules)
        self.assertTrue("DummyModule3" in runtime.service.modules)

        # Try to resolve 3 gives an exception because there is no provider for X
        result = runtime.service.resolve(["DummyModule3"])
        
        
if __name__ == '__main__':
    unittest.main()

