# Generated by Django 4.2.1 on 2023-06-26 14:49

import django.db.models.deletion
import django_fsm
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("djstripe", "0011_2_7"),
        ("qt_auth", "0018_alter_user_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                help_text="The user's Stripe Customer object, if it exists",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="djstripe.customer",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="status",
            field=django_fsm.FSMField(
                choices=[
                    ("registered", "Registered"),
                    ("verified", "Verified"),
                    ("subscribed", "Subscribed"),
                    ("change_email", "Change Email"),
                ],
                default="registered",
                max_length=50,
            ),
        ),
    ]
