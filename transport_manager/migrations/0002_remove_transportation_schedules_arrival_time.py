# Generated by Django 5.1 on 2025-02-13 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport_manager', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transportation_schedules',
            name='arrival_time',
        ),
    ]
