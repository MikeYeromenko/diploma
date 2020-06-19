# Generated by Django 3.0.7 on 2020-06-19 07:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seance', '0003_auto_20200618_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seance',
            name='advertisements_duration',
            field=models.TimeField(blank=True, default=datetime.time(0, 10), null=True, verbose_name='advertisements duration: '),
        ),
        migrations.AlterField(
            model_name='seance',
            name='time_hall_free',
            field=models.TimeField(blank=True, null=True, verbose_name='hall free at: '),
        ),
    ]
