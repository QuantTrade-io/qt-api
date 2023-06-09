# Generated by Django 4.2.1 on 2023-07-05 08:05

from django.db import migrations, models
import django.utils.timezone
import qt_utils.models


class Migration(migrations.Migration):
    dependencies = [
        ("qt_security", "0005_device_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        max_length=250,
                        null=True,
                        storage=qt_utils.models.QTPublicAssets(),
                        upload_to="images/devices/",
                    ),
                ),
                ("description", models.TextField(max_length=1024)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
