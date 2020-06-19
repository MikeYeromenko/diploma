# Generated by Django 3.0.7 on 2020-06-19 07:57

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='email address')),
                ('wallet', models.FloatField(blank=True, null=True, verbose_name='wallet')),
                ('was_deleted', models.BooleanField(default=False, verbose_name='was deleted?')),
                ('last_activity', models.DateTimeField(auto_now_add=True, null=True, verbose_name="user's last activity was: ")),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('starring', models.CharField(max_length=200, verbose_name='starring')),
                ('director', models.CharField(max_length=100, verbose_name='director')),
                ('duration', models.TimeField(verbose_name='duration')),
                ('description', models.TextField(verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='instance created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='instance updated at')),
                ('is_active', models.BooleanField(default=True, verbose_name='in run?')),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='instance created by')),
            ],
        ),
        migrations.CreateModel(
            name='Hall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='name')),
                ('quantity_seats', models.PositiveSmallIntegerField(default=0, verbose_name='how many seats?')),
                ('quantity_rows', models.PositiveSmallIntegerField(default=0, verbose_name='how many rows?')),
                ('description', models.TextField(verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='instance created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='instance updated at')),
                ('is_active', models.BooleanField(default=True, verbose_name='in run?')),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='halls', to=settings.AUTH_USER_MODEL, verbose_name='instance created by')),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='instance created at')),
                ('was_returned', models.BooleanField(default=False, verbose_name='was returned?')),
                ('returned_at', models.DateTimeField(blank=True, null=True, verbose_name='returned at')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchases', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='SeatCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='category name')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='instance created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='instance updated at')),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='seat_categories', to=settings.AUTH_USER_MODEL, verbose_name='instance created by')),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(default=0, verbose_name='number of seat')),
                ('row', models.PositiveSmallIntegerField(default=0, verbose_name='number of row')),
                ('hall', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='seats', to='seance.Hall', verbose_name='hall')),
                ('seat_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='seats', to='seance.SeatCategory', verbose_name='seat category')),
            ],
            options={
                'verbose_name': 'seat',
                'verbose_name_plural': 'seats',
                'ordering': ('row', 'number'),
                'unique_together': {('row', 'number', 'hall')},
            },
        ),
        migrations.CreateModel(
            name='SeanceBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_starts', models.DateField(verbose_name='starts')),
                ('date_ends', models.DateField(blank=True, null=True, verbose_name='ends')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='instance created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='instance updated at')),
                ('is_active', models.BooleanField(default=True, verbose_name='in run?')),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='seances', to='seance.Film', verbose_name='films')),
                ('hall', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='seances', to='seance.Hall', verbose_name='hall')),
            ],
        ),
        migrations.CreateModel(
            name='Seance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_starts', models.TimeField(verbose_name='starts at: ')),
                ('time_ends', models.TimeField(blank=True, null=True, verbose_name='ends at: ')),
                ('time_hall_free', models.TimeField(blank=True, null=True, verbose_name='hall free at: ')),
                ('advertisements_duration', models.TimeField(blank=True, default=datetime.time(0, 10), null=True, verbose_name='advertisements duration: ')),
                ('cleaning_duration', models.TimeField(blank=True, default=datetime.time(0, 10), null=True, verbose_name='cleaning duration: ')),
                ('description', models.TextField(verbose_name='description')),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='seances', to=settings.AUTH_USER_MODEL, verbose_name='instance created by')),
                ('seance_base', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='seances', to='seance.SeanceBase', verbose_name='base seance')),
            ],
            options={
                'verbose_name': 'seance',
                'verbose_name_plural': 'seances',
                'ordering': ('time_starts',),
            },
        ),
        migrations.CreateModel(
            name='price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(verbose_name='price per one seat')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='instance created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='instance updated at')),
                ('seance', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prices', to='seance.Seance', verbose_name='seance')),
                ('seat_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prices', to='seance.SeatCategory', verbose_name='seat category')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_seance', models.DateField(verbose_name='date of seance')),
                ('price', models.FloatField(verbose_name='price')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='instance created at')),
                ('was_returned', models.BooleanField(default=False, verbose_name='was_returned?')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tickets', to='seance.Purchase', verbose_name='purchase')),
                ('seance', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tickets', to='seance.Seance', verbose_name='seance')),
                ('seat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tickets', to='seance.Seat', verbose_name='seat')),
            ],
            options={
                'unique_together': {('seance', 'date_seance', 'seat')},
            },
        ),
    ]
