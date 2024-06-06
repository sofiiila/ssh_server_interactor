import unittest
from pydantic import ValidationError
from model import SecServerConfig  #


class TestSecServerConfig(unittest.TestCase):

    def test_valid_input(self):
        config = SecServerConfig(base_server_path="/server", base_local_path="/local", link_base_path="/link")
        self.assertIsInstance(config, SecServerConfig)

    def test_invalid_input(self):
        with self.assertRaises(ValidationError):
            SecServerConfig(base_server_path="", base_local_path="/local", link_base_path="/link")

        with self.assertRaises(ValidationError):
            SecServerConfig(base_server_path="/server", base_local_path="", link_base_path="/link")

        with self.assertRaises(ValidationError):
            SecServerConfig(base_server_path="/server", base_local_path="/local", link_base_path="")


if __name__ == '__main__':
    unittest.main()
