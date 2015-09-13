from datetime import datetime

__author__ = 'bruceshi'

from django.conf import settings


def setting(key, default):
    return getattr(settings, key, default)


def parse_ts(timestamp):
    return datetime.fromtimestamp(float(timestamp))
