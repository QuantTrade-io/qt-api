# Generated by Django 4.2.1 on 2023-06-28 08:42

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("token_blacklist", "0012_alter_outstandingtoken_user"),
        ("qt_utils", "0005_blacklistedjwttoken"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="blacklistedjwttoken",
            options={
                "verbose_name": "Blacklisted JWT Token",
                "verbose_name_plural": "Blacklisted JWT Tokens",
            },
        ),
        migrations.CreateModel(
            name="Device",
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
                ("os", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=255)),
                ("country", models.CharField(max_length=255)),
                (
                    "token",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="token_blacklist.outstandingtoken",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
