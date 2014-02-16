import unittest

'''
This just aggregates and runs all of the tests from the Test folder
'''

if __name__ == "__main__":
    suite = unittest.TestLoader().discover('./Test', pattern = "*_test.py")
    unittest.TextTestRunner(verbosity=2).run(suite)