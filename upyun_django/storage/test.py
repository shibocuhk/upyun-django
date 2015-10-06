from StringIO import StringIO
import os

from django.test import TestCase

from upyun_django.storage.storage import UpYunStorage

__author__ = 'bruceshi'


class StorageTest(TestCase):
    def setUp(self):
        pass

    def test_curd(self):
        self.storage = UpYunStorage(root='/media/resources')
        name = 'test_create'

        content_str = 'hello world'
        content = StringIO(content_str)
        # assert create
        name = self.storage.save(name, content)
        assert name in self.storage.url(name)

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

        # # assert delete
        # self.storage.delete(name)
        # assert self.storage.exists(name) == False

    def test_token(self):
        self.storage = UpYunStorage(token=os.getenv('UPYUN_HOTLINK_TOKEN'))
        name = 'test'
        content_str = 'hello world'
        content = open('company_logo.png', 'r')
        name = self.storage.save(name, content)
        url = self.storage.url(name)
        import requests
        res = requests.get(url)
