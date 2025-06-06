# Generated by Django 5.1.6 on 2025-05-29 18:07

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_preference'),
    ]

    operations = [
        migrations.AddField(
            model_name='preference',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='preference',
            name='total_searches',
            field=models.IntegerField(default=0),
        ),
    ]
