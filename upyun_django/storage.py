import mimetypes
import os
import time
from tempfile import TemporaryFile

from django.core.files.base import File
from django.conf import settings
from django.core.files.storage import Storage
from upyun import UpYun
from upyun import ED_AUTO
from upyun import UpYunServiceException
from django.utils.encoding import force_bytes

from upyun_django.utils import parse_ts, setting, hotlink_signature

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class UpYunStorageFile(File):
    def __init__(self, name, storage, mode='rb'):
        self._file = None
        self._storage = storage
        self.name = name
        self.mode = mode
        self.is_dirty = False

    @property
    def size(self):
        return self._storage.size(self.name)

    # inspired by https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto.py
    def read(self, *args, **kwargs):
        if 'r' not in self.mode:
            raise AttributeError("File was not opened in read mode.")
        return super(UpYunStorageFile, self).read(*args, **kwargs)

    def write(self, content, *args, **kwargs):
        if 'w' not in self.mode:
            raise AttributeError("File was not opened in write mode")
        self.is_dirty = True
        return super(UpYunStorageFile, self).write(force_bytes(content), *args, **kwargs)

    def close(self):
        if self.is_dirty:
            self._file.seek(0)
            self._storage.delete(self.name)
            self._storage.save(self.name, self._file)
        return super(UpYunStorageFile, self).close()

    def _get_file(self):
        if self._file is None:
            self._file = TemporaryFile(suffix='.UpYunStorageFile')
            self._storage.api.get(self._storage.save_key(self.name), self._file)
            self._file.seek(0)
        return self._file

    def _set_file(self, value):
        self._file = value

    def _del_file(self):
        self._storage.delete(self.name)

    def _get_path(self):
        return self._storage.path(self.name)

    def _get_url(self):
        return self._storage.url(self.name)

    file = property(_get_file, _set_file, _del_file)


class UpYunStorage(Storage):
    def __init__(self, username=None, password=None, bucket=None, root='/', timeout=60, endpoint=ED_AUTO, secret=None,
                 token=None, domain=None):
        self._username = username or settings.UPYUN_USERNAME
        self._password = password or settings.UPYUN_PASSWORD
        self._bucket = bucket or settings.UPYUN_BUCKET
        self._hotlink_token = token or setting('UPYUN_HOTLINK_TOKEN', None)
        self._hotlink_token_expire = setting('UPYUN_HOTLINK_TOKEN_EXPIRE', 600)
        self._thumbnail_seperate = setting("UPYUN_THUMBNAIL_SEPERATE", '!')
        self._endpoint = endpoint
        self._domain = domain or 'b0.upaiyun.com'
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
                self._endpoint,
                human=True,
            )
        return self._api

    @property
    def entries(self):
        if self._entries is None:
            self._entries = self._get_or_create_folder()
        return self._entries

    def _open(self, name, mode):
        upyun_file = UpYunStorageFile(name, self, mode)
        return upyun_file

    def _save(self, name, content):
        clean_name = self._clean_name(name)
        content_type = getattr(content, 'content_type', mimetypes.guess_type(name)[0] or 'text/plain')
        headers = {
            'Mkdir': True,
            'Content-Type': content_type,
        }
        content.seek(0)
        self.api.put(self._save_key(clean_name), content, headers=headers, secret=self._secret)

        return clean_name

    def delete(self, name):
        self.api.delete(self._save_key(self._clean_name(name)))

    def exists(self, name):
        try:
            return self._get_or_update_entry(name)
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
            entry['name'] = os.path.join(path, entry['name'])
            if entry['type'] == 'N':
                files.add(entry['name'])
            else:
                dirs.add(entry['name'])

            self.entries.update(dict([self._entry_to_tuple(entry)]))
        return list(dirs), list(files)

    def size(self, name):
        return self._get_or_update_entry(name)['size']

    def modified_time(self, name):
        return parse_ts(self._get_or_update_entry(name)['time'])

    def url(self, name):
        _upt = self._upt_token(name)
        _secret = (self._thumbnail_seperate + self._secret) if self._secret else ''
        return 'http://%s.%s%s%s%s' % (self._bucket, self._domain, self._save_key(name), _secret, '?_upt=' + _upt)

    def thumbnail_url(self, name, version):
        _upt = self._upt_token(name)
        return 'http://%s.%s%s!%s%s' % (self._bucket, self._domain, self._save_key(name), version, '?_upt=' + _upt)

    def save_key(self, name):
        return self._save_key(name)

    def set_secret(self, secret):
        self._secret = secret

    def path(self, name):
        return self.save_key(name)

    def _clean_name(self, name):
        return os.path.normpath(name).replace("\\", "/")

    def _upt_token(self, name):
        _upt = hotlink_signature(self._save_key(name), self._hotlink_token,
                                 int(time.time()) + self._hotlink_token_expire) if self._hotlink_token else ''

        return _upt

    def _save_key(self, name):
        return os.path.join(self._root, name)

    def _get_or_create_folder(self):
        try:
            res = dict(self._entry_to_tuple(entry) for entry in self.api.getlist(self._root))
        except UpYunServiceException as ex:
            if ex.status == 404:
                self.api.mkdir(self._root)
                res = dict(self._entry_to_tuple(entry) for entry in self.api.getlist(self._root))
            else:
                raise
        return res

    def _get_or_update_entry(self, name):
        save_key = self._save_key(self._clean_name(name))
        if save_key in self.entries:
            return self.entries[save_key]
        else:
            entry = self._file_info_to_entry(name, self.api.getinfo(save_key))
            self.entries.update(dict([self._entry_to_tuple(entry)]))
            return entry

    def _entry_to_tuple(self, entry):
        return self._save_key(entry['name'] if entry['type'] == 'N' else entry['name'] + '/'), entry

    def _file_info_to_entry(self, name, file_info):
        return {
            'type': 'N',
            'size': file_info['file-size'],
            'time': file_info['file-date'],
            'name': name
        }


class UpYunStaticStorage(UpYunStorage):
    def __init__(self):
        root = setting('UPYUN_STATIC_ROOT', '/static')
        super(UpYunStaticStorage, self).__init__(root=root)
        dirs = self.listdir(root)[0]
        while len(dirs) != 0:
            path = dirs.pop()
            print(path)
            dirs.extend(self.listdir(path)[0])
