# Generated by Django 5.0.6 on 2024-08-25 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0025_alter_availablecourse_students_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='availablecourse',
            name='date',
            field=models.TextField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='availablecourse',
            name='start_date',
            field=models.DateField(blank=True, default=None),
        ),
    ]
