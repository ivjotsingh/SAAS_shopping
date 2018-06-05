# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0025_postmodel_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postmodel',
            name='amount',
            field=models.FloatField(),
        ),
    ]
