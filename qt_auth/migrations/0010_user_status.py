# Generated by Django 4.2 on 2023-05-12 08:57

import django_fsm
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("qt_auth", "0009_delete_newslettersubscriber"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="status",
            field=django_fsm.FSMField(
                choices=[
                    ("R", "Registered"),
                    ("V", "Verified"),
                    ("S", "Subscribed"),
                    ("U", "Unsubscribed"),
                ],
                default="R",
                max_length=50,
            ),
        ),
    ]
