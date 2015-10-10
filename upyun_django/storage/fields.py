from django.db.models.fields.files import FieldFile, FileDescriptor
from django.db.models import FileField
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from upyun_django.storage.storage import UpYunStorage
from upyun_django.storage.utils import setting


class UpYunFieldFile(FieldFile):
    def __init__(self, instance, field, name):
        super(UpYunFieldFile, self).__init__(instance, field, name)

    def thumbnail(self, version):
        return self.storage.thumbnail_url(self.name, version)


class UpYunFileDescriptor(FileDescriptor):
    pass


class UpYunFileField(FileField):
    attr_class = UpYunFieldFile
    descriptor_class = UpYunFileDescriptor

    description = _('UpYun File')

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        storage = UpYunStorage(root=(setting('UPYUN_MEDIA_ROOT', settings.MEDIA_ROOT)))
        super(UpYunFileField, self).__init__(verbose_name, name, upload_to, storage, **kwargs)

    def get_internal_type(self):
        return 'UpYunFileField'

    def db_type(self, connection):
        return 'varchar'
