# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0023_auto_20170808_2351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentmodel',
            name='review',
            field=models.CharField(max_length=20),
        ),
    ]
