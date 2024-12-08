# Generated by Django 5.1.3 on 2024-11-24 04:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SchedulerApp', '0004_remove_course_has_lab_course_number_of_classes_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='number_of_classes',
        ),
        migrations.AddField(
            model_name='course',
            name='number_of_labs',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]