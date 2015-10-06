__author__ = 'bruceshi'
from django.db import models


class UpYunToken(models.Model):
    key = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    expire = models.IntegerField(default=600)
    timestamp = models.DateTimeField(auto_now=True)
