__author__ = 'bruceshi'
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CHARSET = "UTF-8"

SECRET_KEY = 'uondwoapip98908241hrlkao[doadhwadhiuwdywgi]'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
INSTALLED_APPS = {
    'storage'
}
