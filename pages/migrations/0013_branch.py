# Generated by Django 5.0.6 on 2024-08-06 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0012_availablecourse_start_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
    ]
