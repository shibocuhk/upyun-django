# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UpYunToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=255)),
                ('token', models.CharField(max_length=255)),
                ('expire', models.IntegerField(default=600)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
