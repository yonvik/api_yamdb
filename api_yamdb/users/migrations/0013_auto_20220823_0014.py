# Generated by Django 2.2.16 on 2022-08-22 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20220823_0006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='confirmation_code',
            field=models.CharField(db_index=True, max_length=256, null=True, unique=True),
        ),
    ]
