# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0024_auto_20180307_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='postmodel',
            name='amount',
            field=models.FloatField(default=0),
        ),
    ]
