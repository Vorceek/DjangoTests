# Generated by Django 5.1.3 on 2025-02-24 19:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0002_periodo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='periodo',
            old_name='periodo',
            new_name='nome',
        ),
    ]
