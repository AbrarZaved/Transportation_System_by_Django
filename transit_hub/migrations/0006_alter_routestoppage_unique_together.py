# Generated by Django 5.1 on 2025-02-15 07:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transit_hub', '0005_alter_routestoppage_created_at'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='routestoppage',
            unique_together=set(),
        ),
    ]
