# Generated by Django 5.0.6 on 2024-07-28 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_alter_mainpostforbot_entities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainpostforbot',
            name='entities',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
