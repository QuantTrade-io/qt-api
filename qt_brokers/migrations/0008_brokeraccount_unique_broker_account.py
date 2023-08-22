# Generated by Django 4.2.1 on 2023-08-21 08:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("qt_brokers", "0007_brokeraccount_email"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="brokeraccount",
            constraint=models.UniqueConstraint(
                fields=("broker", "authentication_method", "email", "username"),
                name="unique_broker_account",
            ),
        ),
    ]
