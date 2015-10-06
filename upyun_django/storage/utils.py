from datetime import datetime
import hashlib

__author__ = 'bruceshi'

from django.conf import settings


def setting(key, default):
    return getattr(settings, key, default)


def parse_ts(timestamp):
    return datetime.fromtimestamp(float(timestamp))


def hotlink_signature(url, token, etime):
    if not url.startswith('/'):
        url = '/' + url
    print '%s %s %s' % (url, token, etime)
    return hashlib.md5('&'.join([token, str(etime), url])).hexdigest()[12:20] + str(etime)
