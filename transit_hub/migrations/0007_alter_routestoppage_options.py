# Generated by Django 5.1 on 2025-02-15 09:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transit_hub', '0006_alter_routestoppage_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='routestoppage',
            options={'ordering': ['-created_at']},
        ),
    ]
