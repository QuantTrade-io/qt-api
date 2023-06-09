# Generated by Django 4.2 on 2023-04-15 08:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("djstripe", "0011_2_7"),
        (
            "qt_auth",
            "0002_user_are_guidelines_accepted_user_is_email_verified_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_subscription_paid",
        ),
        migrations.AddField(
            model_name="user",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                help_text="The user's Stripe Customer object, if it exists",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="djstripe.customer",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="subscription",
            field=models.ForeignKey(
                blank=True,
                help_text="The user's Stripe Subscription object, if it exists",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="djstripe.subscription",
            ),
        ),
    ]
