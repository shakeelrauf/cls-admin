# Generated by Django 3.1.7 on 2021-02-22 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sheet',
            old_name='name',
            new_name='config_name',
        ),
        migrations.AddField(
            model_name='sheet',
            name='display_name',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]