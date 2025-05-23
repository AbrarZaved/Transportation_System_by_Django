# Generated by Django 5.1 on 2025-02-13 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport_manager', '0002_remove_transportation_schedules_arrival_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='transportation_schedules',
            name='audience',
            field=models.CharField(choices=[('employee', 'Employees'), ('student', 'Students'), ('female_only', 'Female Only')], default='student', max_length=20),
        ),
        migrations.AddField(
            model_name='transportation_schedules',
            name='from_dsc',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='transportation_schedules',
            name='to_dsc',
            field=models.BooleanField(default=False),
        ),
    ]
