# Generated by Django 3.0.7 on 2020-06-27 06:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seance', '0008_auto_20200622_0851'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='price',
            options={'ordering': ('price',)},
        ),
    ]
