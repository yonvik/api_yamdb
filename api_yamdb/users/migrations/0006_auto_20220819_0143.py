# Generated by Django 3.2.15 on 2022-08-18 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20220817_0015'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'Пользователь'), ('moderator', 'Модератор '), ('admin', 'Администратор')], default='user', max_length=20),
        ),
        migrations.AlterField(
            model_name='user',
            name='secret_key',
            field=models.CharField(db_index=True, max_length=256, null=True, unique=True),
        ),
    ]