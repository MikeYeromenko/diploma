# Generated by Django 3.0.7 on 2020-06-18 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seance', '0002_auto_20200618_1847'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='total_price',
        ),
        migrations.AddField(
            model_name='ticket',
            name='price',
            field=models.FloatField(default=100, verbose_name='price'),
            preserve_default=False,
        ),
    ]
