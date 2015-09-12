import mimetypes
import os

from django.core.files.base import File

__author__ = 'bruceshi'
from django.conf import settings
from django.core.files.storage import Storage
from upyun import UpYun
from upyun import ED_AUTO
from upyun import UpYunServiceException


class UpYunStorageFile(File):
    pass


class UpYunStorage(Storage):
    def __init__(self, username, password, bucket, root='/', timeout=60, endpoint=ED_AUTO, secret=None):
        self._username = username or settings.UPYUN_USERNAME
        self._password = password or settings.UPYUN_PASSWORD
        self._bucket = bucket or self.UPYUN_BUCKET
        self._endpoint = endpoint
        self._timeout = timeout
        self._root = root
        self._api = None
        self._secret = secret
        self._entries = None

    @property
    def api(self):
        if self._api is None:
            self._api = UpYun(
                self._bucket,
                self._username,
                self._password,
                self._timeout,
                self._endpoint
            )
        return self._api

    @property
    def entries(self):
        if self._entries is None:
            self._entries = self._get_or_create_folder()
        return self._entries

    def _save(self, name, content):
        clean_name = self._clean_name(name)
        content_type = getattr(content, 'content_type', mimetypes.guess_type(name)[0] or 'image/jpeg')
        headers = {
            'Mkdir': True,
            'Content-Type': content_type,
        }

        self.api.put(self._save_key(clean_name), content, headers=headers, secret=self._secret)

        return clean_name

    def delete(self, name):
        self.api.delete(self._save_key(self._clean_name(name)))

    def exists(self, name):
        try:
            self.api.getinfo(self._save_key(self._clean_name(name)))
            return True
        except UpYunServiceException as ex:
            if ex.status == 404:
                return False
            else:
                raise

    def listdir(self, path):
        if not path.endswith('/'):
            path += '/'
        res = self.api.getlist(self._save_key(self._clean_name(path)))

        dirs = set()
        files = set()
        for entry in res:
            if entry['type'] == 'N':
                files.add(entry['name'])
            else:
                dirs.add(entry['name'])
        return list(dirs), list(files)

    def _clean_name(self, name):
        return os.path.normpath(name).replace("\\", "/")

    def _save_key(self, name):
        return os.path.join(self._root, name)

    def _get_or_create_folder(self):
        try:
            res = dict((entry['name'], entry) for entry in self.api.getlist(self._root))
        except UpYunServiceException as ex:
            if ex.status == 404:
                self.api.mkdir(self._root)
                res = dict((entry['name'], entry) for entry in self.api.getlist(self._root))
            else:
                raise
        return res
