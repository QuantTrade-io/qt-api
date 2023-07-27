# Generated by Django 4.2.1 on 2023-07-27 03:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("token_blacklist", "0012_alter_outstandingtoken_user"),
        ("qt_security", "0010_alter_device_unique_together_session_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session",
            name="token",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="session",
                to="token_blacklist.outstandingtoken",
            ),
        ),
    ]
