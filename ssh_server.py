import os
import paramiko


class SshServerTransport:

    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        self.client.connect(self.host, username=self.username, password=self.password, port=self.port)

    def disconnect(self):
        self.client.close()

    def is_object_exist(self, serverpath_object, flag):
        ...

    def delete_object(self, serverpath_object, flag):
        ...

    def scp_object(self, localpath_object, serverpath_object, base_server_path):
        ...

    def list_objects_of_dir(self, serverpath_dir):
        ...

    def relative_link_object(self, link_object, serverpath_link, relative_path):
        ...

    def absolute_link_object(self, link_object, serverpath_link):
        ...


class ObjectsFlags:
    FILE_FLAG = 0o100000
    DIR_FLAG = 0o040000
    LINK_FLAG = 0o120000


class ObjectExist(Exception):
    def __init__(self, path):
        self.path = path
        super().__init__(f'Объект на этом пути {path} уже существует')


class ObjectNotExist(Exception):
    def __init__(self, path):
        self.path = path
        super().__init__(f'Объект на этом пути {path} еще не существует')


class SshServerInteractor:

    def __init__(self, transport: SshServerTransport):
        self.transport = transport

    def delete(self, serverpath_object: str, flag: ObjectsFlags):
        if self.transport.is_object_exist(serverpath_object=serverpath_object, flag=flag):
            self.transport.delete_object(serverpath_object=serverpath_object, flag=flag)
            if self.transport.is_object_exist(serverpath_object=serverpath_object, flag=flag):
                raise ObjectExist(path=serverpath_object)
        else:
            raise ObjectNotExist(path=serverpath_object)

    def upload(self, localpath_object: str, serverpath_object: str, base_server_path: str):
        if self.transport.is_object_exist(serverpath_object=serverpath_object, flag=ObjectsFlags.DIR_FLAG):
            raise ObjectExist(path=serverpath_object)
        self.transport.scp_object(localpath_object=localpath_object, serverpath_object=serverpath_object,
                                  base_server_path=base_server_path)
        if not self.transport.is_object_exist(serverpath_object, flag=ObjectsFlags.DIR_FLAG):
            raise ObjectNotExist(path=serverpath_object)

    def get_list_of_objects_in_dir(self, serverpath_dir: str):
        if self.transport.is_object_exist(serverpath_object=serverpath_dir, flag=ObjectsFlags.DIR_FLAG):
            return self.transport.list_objects_of_dir(serverpath_dir=serverpath_dir)
        raise ObjectNotExist(path=serverpath_dir)

    def relative_link_object(self, base_serverpath: str, object_name: str, serverpath_link: str):
        link_object = os.path.join(base_serverpath, object_name)
        new_link = os.path.join(serverpath_link, object_name)
        relative_path = os.path.relpath(link_object, serverpath_link)
        if self.transport.is_object_exist(serverpath_object=link_object, flag=ObjectsFlags.DIR_FLAG):
            if self.transport.is_object_exist(serverpath_object=new_link, flag=ObjectsFlags.LINK_FLAG):
                raise ObjectExist(path=new_link)
            self.transport.relative_link_object(link_object=link_object, serverpath_link=serverpath_link,
                                                relative_path=relative_path)
            if not self.transport.is_object_exist(serverpath_object=new_link, flag=ObjectsFlags.DIR_FLAG):
                raise ObjectNotExist(path=new_link)
        else:
            raise ObjectNotExist(path=link_object)

    def absolute_link_object(self, base_serverpath: str, object_name: str, serverpath_link: str):
        link_object = os.path.join(base_serverpath, object_name)
        new_link = os.path.join(serverpath_link, object_name)
        if self.transport.is_object_exist(serverpath_object=link_object, flag=ObjectsFlags.DIR_FLAG):
            if self.transport.is_object_exist(serverpath_object=new_link, flag=ObjectsFlags.LINK_FLAG):
                raise ObjectExist(path=new_link)
            self.transport.absolute_link_object(
                link_object=link_object,
                serverpath_link=serverpath_link
            )
            if not self.transport.is_object_exist(serverpath_object=new_link, flag=ObjectsFlags.DIR_FLAG):
                raise ObjectNotExist(path=new_link)
        else:
            raise ObjectNotExist(path=link_object)
