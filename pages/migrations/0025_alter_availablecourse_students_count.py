# Generated by Django 5.0.6 on 2024-08-25 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0024_alter_availablecourse_students'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availablecourse',
            name='students_count',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
