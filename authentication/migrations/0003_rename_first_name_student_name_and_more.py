# Generated by Django 5.1.6 on 2025-05-27 05:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_student'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='first_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='student',
            name='last_name',
        ),
    ]
