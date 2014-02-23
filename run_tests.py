import unittest
from Test import models_test, postprocessing_test, planner_test

'''
This just aggregates and runs all of the tests from the Test folder
'''

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule(models_test)
    suite.addTests(unittest.TestLoader().loadTestsFromModule(postprocessing_test))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(planner_test))
    unittest.TextTestRunner(verbosity=2).run(suite)