# Generated by Django 4.2.1 on 2023-07-05 19:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("qt_security", "0006_deviceimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="device",
            name="user_agent",
            field=models.CharField(default=1, max_length=510),
            preserve_default=False,
        ),
    ]