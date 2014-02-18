import unittest
from Test import models_test

'''
This just aggregates and runs all of the tests from the Test folder
'''

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule(models_test)
    unittest.TextTestRunner(verbosity=2).run(suite)