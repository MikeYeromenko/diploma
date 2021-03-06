# Generated by Django 3.0.7 on 2020-06-22 06:07

import colorfield.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seance', '0006_auto_20200621_0638'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'ordering': ('-date_seance',)},
        ),
        migrations.AddField(
            model_name='seatcategory',
            name='color',
            field=colorfield.fields.ColorField(default='#FFEFEF', max_length=18),
        ),
        migrations.AlterField(
            model_name='seancebase',
            name='film',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='base_seances', to='seance.Film', verbose_name='film'),
        ),
        migrations.AlterField(
            model_name='seancebase',
            name='hall',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='base_seances', to='seance.Hall', verbose_name='hall'),
        ),
        migrations.AlterField(
            model_name='seat',
            name='seat_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seats', to='seance.SeatCategory', verbose_name='seat category'),
        ),
    ]
