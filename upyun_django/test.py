import django

__author__ = 'bruceshi'

import os
import sys

from django.conf import settings

BASE_PATH = os.path.dirname(__file__)


def main():
    """
    Standalone django model test with a 'memory-only-django-installation'.
    You can play with a django model without a complete django app installation.
    http://www.djangosnippets.org/snippets/1044/
    """
    settings.configure(
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.sessions',
            'django.contrib.contenttypes',
            'upyun',
        ),
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        ROOT_URLCONF='beproud.django.authutils.tests.test_urls',
        DEFAULT_FILE_STORAGE='django_upyun.UpYunStorage',
        UPYUN_USERNAME=os.getenv('UPYUN_USERNAME'),
        UPYUN_PASSWORD=os.getenv('UPYUN_PASSWORD'),
        UPYUN_BUCKET=os.getenv('UPYUN_BUCKET'),
        MEDIA_URL="http://%s.b0.upaiyun.com/media/" % os.getenv('UPYUN_BUCKET'),
        STATIC_URL="http://%s.b0.upaiyun.com/static/" % os.getenv('UPYUN_BUCKET')
    )
    django.setup()
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)

    failures = test_runner.run_tests(['upyun'])
    sys.exit(failures)


if __name__ == '__main__':
    main()
