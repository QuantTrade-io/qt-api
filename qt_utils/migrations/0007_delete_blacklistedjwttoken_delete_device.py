# Generated by Django 4.2.1 on 2023-06-28 09:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("qt_utils", "0006_alter_blacklistedjwttoken_options_device"),
    ]

    operations = [
        migrations.DeleteModel(
            name="BlacklistedJWTToken",
        ),
        migrations.DeleteModel(
            name="Device",
        ),
    ]
