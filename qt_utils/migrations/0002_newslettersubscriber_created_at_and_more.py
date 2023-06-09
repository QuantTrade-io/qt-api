# Generated by Django 4.2 on 2023-05-11 03:39

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("qt_utils", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="newslettersubscriber",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.AddField(
            model_name="newslettersubscriber",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
