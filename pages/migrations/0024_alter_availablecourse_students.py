# Generated by Django 5.0.6 on 2024-08-25 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0023_availablecourse_description_entities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availablecourse',
            name='students',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
