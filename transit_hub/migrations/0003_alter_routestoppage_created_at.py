# Generated by Django 5.1 on 2025-02-15 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transit_hub', '0002_stoppage_remove_route_route_distance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routestoppage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
