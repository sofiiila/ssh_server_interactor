import os.path
import unittest
BASE_DIR = "/home/sofi/PycharmProjects/ssh_Server/"

TEST_FOLDER = os.path.join(BASE_DIR, 'tests')

if __name__ == '__main__':
    tests = unittest.TestLoader().discover(TEST_FOLDER)
    unittest.TextTestRunner(verbosity=2).run(tests)
