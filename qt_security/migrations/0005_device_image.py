# Generated by Django 4.2.1 on 2023-07-05 06:35

from django.db import migrations, models
import qt_utils.models


class Migration(migrations.Migration):
    dependencies = [
        ("qt_security", "0004_rename_family_device_info_remove_device_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="device",
            name="image",
            field=models.ImageField(
                blank=True,
                max_length=250,
                null=True,
                storage=qt_utils.models.QTPublicAssets(),
                upload_to="images/devices/",
            ),
        ),
    ]