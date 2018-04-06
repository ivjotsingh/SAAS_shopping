# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-30 19:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0008_auto_20170730_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment_model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('text', models.CharField(max_length=255)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.Post_model')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.User_model')),
            ],
        ),
    ]
