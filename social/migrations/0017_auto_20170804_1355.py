# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 08:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0016_commentmodel_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentmodel',
            name='review',
            field=models.FloatField(),
        ),
    ]