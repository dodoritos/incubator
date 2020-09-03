# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-10-01 15:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0011_auto_20190503_1346'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='nbr_revision',
        ),
        migrations.RemoveField(
            model_name='historicalarticle',
            name='nbr_revision',
        ),
        migrations.AddField(
            model_name='article',
            name='last_modifier',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='last_modifier',
            field=models.CharField(default='', max_length=50),
        ),
    ]
