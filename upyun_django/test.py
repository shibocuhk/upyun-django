from StringIO import StringIO

from django.test import TestCase

from upyun_django.storage import UpYunStorage

__author__ = 'bruceshi'


class StorageTest(TestCase):
    def setUp(self):
        self.storage = UpYunStorage()

    def test_curd(self):
        name = 'test'
        content_str = 'hello world'
        content = StringIO(content_str)
        # assert create
        name = self.storage.save(name, content)
        assert self.storage.url(name).endswith(name)

        # assert open
        remote_file = self.storage.open(name, 'rb')
        assert remote_file.read() == content_str
        remote_file.close()

        # assert update
        remote_file = self.storage.open(name, 'wb')
        another_content_str = 'another content'
        another_content = StringIO(another_content_str)
        remote_file.write(another_content.read())
        remote_file.close()
        assert self.storage.open(name, 'rb').read() == another_content_str

        # assert delete
        self.storage.delete(name)
        assert self.storage.exists(name) == False
