import unittest
import tests


testLoad = unittest.TestLoader()
suites = testLoad.loadTestsFromModule(tests)

runner = unittest.TextTestRunner(verbosity=2)
runner.run(suites)
