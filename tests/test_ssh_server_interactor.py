import unittest
from unittest.mock import Mock, patch, call
from ssh_server import SshServerInteractor, SshServerTransport, ObjectsFlags, ObjectExist, ObjectNotExist


class TestSshServerInteractor(unittest.TestCase):
    def setUp(self):
        self.transport = Mock(spec=SshServerTransport)
        self.interactor = SshServerInteractor(self.transport)

    @patch('os.path')
    def test_delete_existing_object(self, mock_os_path):
        mock_os_path.join.return_value = 'serverpath_object'
        self.transport.is_object_exist.side_effect = [True, False, False]
        self.transport.delete_object.return_value = None

        self.interactor.delete('serverpath_object', ObjectsFlags.DIR_FLAG)

        self.transport.is_object_exist.assert_called_with(serverpath_object='serverpath_object',
                                                              flag=ObjectsFlags.DIR_FLAG)
        self.transport.delete_object.assert_called_with(serverpath_object='serverpath_object',
                                                            flag=ObjectsFlags.DIR_FLAG)
        self.transport.is_object_exist.assert_called_with(serverpath_object='serverpath_object',
                                                              flag=ObjectsFlags.DIR_FLAG)
        self.assertFalse(
            self.transport.is_object_exist(serverpath_object='serverpath_object', flag=ObjectsFlags.DIR_FLAG))

    @patch('os.path')
    def test_delete_non_existing_object(self, mock_os_path):
        mock_os_path.join.return_value = 'serverpath_object'
        self.transport.is_object_exist.return_value = False

        with self.assertRaises(ObjectNotExist) as context:
            self.interactor.delete('serverpath_object', ObjectsFlags.DIR_FLAG)

        self.assertEqual(context.exception.path, 'serverpath_object')
        self.transport.is_object_exist.assert_called_with(serverpath_object='serverpath_object',
                                                          flag=ObjectsFlags.DIR_FLAG)
        self.transport.delete_object.assert_not_called()

    @patch('os.path')
    @patch('ssh_server.SshServerTransport')
    def test_upload_new_object(self, mock_transport, mock_os_path):
        mock_os_path.join.return_value = 'serverpath_object'
        mock_transport.return_value.is_object_exist.side_effect = [False, True]
        mock_transport.return_value.scp_object.return_value = None

        self.interactor = SshServerInteractor(mock_transport.return_value)
        self.interactor.upload('localpath_object', 'serverpath_object', 'base_server_path')

        mock_transport.return_value.is_object_exist.assert_called_with('serverpath_object',
                                                                       flag=ObjectsFlags.DIR_FLAG)
        mock_transport.return_value.scp_object.assert_called_with(localpath_object='localpath_object',
                                                                  serverpath_object='serverpath_object',
                                                                  base_server_path='base_server_path')
        mock_transport.return_value.is_object_exist.assert_called_with('serverpath_object',
                                                                       flag=ObjectsFlags.DIR_FLAG)
        self.assertTrue(mock_transport.return_value.is_object_exist.call_args_list[-1][1]['flag'])

    @patch('os.path')
    def test_upload_existing_object(self, mock_os_path):
        mock_os_path.join.return_value = 'serverpath_object'
        self.transport.is_object_exist.return_value = True

        with self.assertRaises(ObjectExist) as context:
            self.interactor.upload('localpath_object',
                                   'serverpath_object',
                                   'base_server_path')

        self.assertEqual(context.exception.path, 'serverpath_object')
        self.transport.is_object_exist.assert_called_with(serverpath_object='serverpath_object',
                                                          flag=ObjectsFlags.DIR_FLAG)
        self.transport.scp_object.assert_not_called()

    @patch('os.path')
    @patch('ssh_server.SshServerTransport')
    def test_get_list_of_objects_in_dir(self, mock_transport, mock_os_path):
        mock_os_path.join.return_value = 'serverpath_dir'
        mock_transport.return_value.is_object_exist.return_value = True
        mock_transport.return_value.list_objects_of_dir.return_value = ['object1', 'object2']

        self.interactor = SshServerInteractor(mock_transport.return_value)
        result = self.interactor.get_list_of_objects_in_dir('serverpath_dir')

        mock_transport.return_value.is_object_exist.assert_called_with(serverpath_object='serverpath_dir',
                                                                       flag=ObjectsFlags.DIR_FLAG)
        mock_transport.return_value.list_objects_of_dir.assert_called_with(serverpath_dir='serverpath_dir')
        self.assertEqual(result, ['object1', 'object2'])

    @patch('os.path')
    @patch('ssh_server.SshServerTransport')
    def test_relative_link_object(self, mock_transport, mock_os_path):
        mock_os_path.join.side_effect = ['link_object', 'new_link']
        mock_os_path.relpath.return_value = 'relative_path'
        mock_transport.return_value.is_object_exist.side_effect = [
            True,
            False,
            True
        ]
        mock_transport.return_value.relative_link_object.return_value = None

        self.interactor = SshServerInteractor(mock_transport.return_value)
        self.interactor.relative_link_object('base_serverpath', 'object_name', 'serverpath_link')

        mock_transport.return_value.is_object_exist.assert_has_calls([
            call(flag=ObjectsFlags.DIR_FLAG, serverpath_object='link_object'),
            call(flag=ObjectsFlags.LINK_FLAG, serverpath_object='new_link'),
            call(flag=ObjectsFlags.DIR_FLAG, serverpath_object='new_link')
        ])
        mock_transport.return_value.relative_link_object.assert_called_with(
            link_object='link_object',
            serverpath_link='serverpath_link',
            relative_path='relative_path'
        )
        self.assertTrue(mock_transport.return_value.is_object_exist.call_args_list[-1][1]['flag'])

    @patch('os.path')
    @patch('ssh_server.SshServerTransport')
    def test_absolute_link_object(self, mock_transport, mock_os_path):
        mock_os_path.join.side_effect = ['link_object', 'new_link']
        mock_transport.return_value.is_object_exist.side_effect = [True, False, True]
        mock_transport.return_value.absolute_link_object.return_value = None

        self.interactor = SshServerInteractor(mock_transport.return_value)
        self.interactor.absolute_link_object('base_serverpath', 'object_name', 'serverpath_link')

        mock_transport.return_value.is_object_exist.assert_has_calls([
            call(flag=ObjectsFlags.DIR_FLAG, serverpath_object='link_object'),
            call(flag=ObjectsFlags.LINK_FLAG, serverpath_object='new_link'),
            call(flag=ObjectsFlags.DIR_FLAG, serverpath_object='new_link')
        ])
        mock_transport.return_value.absolute_link_object.assert_called_with(
            link_object='link_object',
            serverpath_link='serverpath_link'
        )
        self.assertTrue(mock_transport.return_value.is_object_exist.call_args_list[-1][1]['flag'])


if __name__ == '__main__':
    unittest.main()
