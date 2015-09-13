import mimetypes
import os
from tempfile import TemporaryFile

from django.utils.encoding import force_bytes

from upyun_django.utils import parse_ts

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.core.files.base import File

__author__ = 'bruceshi'
from django.conf import settings
from django.core.files.storage import Storage
from upyun import UpYun
from upyun import ED_AUTO
from upyun import UpYunServiceException


class UpYunStorageFile(File):
    def __init__(self, name, storage, mode):
        self._name = name
        self._storage = storage
        self._mode = mode
        self._file = None
        self._is_dirty = False

    @property
    def size(self):
        return self._storage.size(self._name)

    # inspired by https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto.py
    def read(self, *args, **kwargs):
        if 'r' not in self._mode:
            raise AttributeError("File was not opened in read mode.")
        return super(UpYunStorageFile, self).read(*args, **kwargs)

    def write(self, content, *args, **kwargs):
        if 'w' not in self._mode:
            raise AttributeError("File was not opened in write mode")
        self._is_dirty = True
        return super(UpYunStorageFile, self).write(force_bytes(content), *args, **kwargs)

    def close(self):
        if self._is_dirty:
            self._storage.save(self._name, self.file)

    def _get_file(self):
        if self._file is None:
            self._file = TemporaryFile(suffix='.UpYunStorageFile')
            self._storage.api.get(self._storage.save_key(self._name), self._file)
            self._file.seek(0)
        return self._file

    def _set_file(self, value):
        self._file = value

    file = property(_get_file, _set_file)


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

    def _open(self, name, mode):
        upyun_file = UpYunStorageFile(name, 'rb')
        return upyun_file

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

            self.entries.update(dict(self._entry_to_tuple(entry)))
        return list(dirs), list(files)

    def size(self, name):
        return self._get_or_update_entry(name)['size']

    def modified_time(self, name):
        return parse_ts(self._get_or_update_entry(name)['time'])

    def url(self, name):
        return 'http://%s.%s/%s' % (self._bucket, self._endpoint, self._save_key(name))

    def save_key(self, name):
        return self._save_key(name)

    def _clean_name(self, name):
        return os.path.normpath(name).replace("\\", "/")

    def _save_key(self, name):
        return os.path.join(self._root, name)

    def _get_or_create_folder(self):
        try:
            res = dict(
                self._entry_to_tuple(entry) for entry in
                self.api.getlist(self._root))
        except UpYunServiceException as ex:
            if ex.status == 404:
                self.api.mkdir(self._root)
                res = dict((entry['name'], entry) for entry in self.api.getlist(self._root))
            else:
                raise
        return res

    def _get_or_update_entry(self, name):
        save_key = self._save_key(self._clean_name(name))
        if save_key in self.entries:
            return self.entries[save_key]
        else:
            entry = self.api.getinfo(save_key)
            self.entries.update(dict(self._entry_to_tuple(entry)))
            return entry

    def _entry_to_tuple(self, entry):
        return self._save_key(entry['name'] if entry['type'] == 'N' else entry['name'] + '/'), entry
