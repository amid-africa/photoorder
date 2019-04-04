# Generated by Django 2.2rc1 on 2019-04-04 17:48

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('name', models.CharField(max_length=128, verbose_name='name known by')),
                ('is_active', models.BooleanField(default=True, verbose_name='active user')),
                ('is_confirmed', models.BooleanField(default=False, verbose_name='email confirmed')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff user')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='super user')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'ordering': ('name',),
            },
            managers=[
                ('objects', user.models.CustomUserManager()),
            ],
        ),
    ]
