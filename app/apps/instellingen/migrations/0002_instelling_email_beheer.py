# Generated by Django 3.2.16 on 2024-07-08 14:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("instellingen", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="instelling",
            name="email_beheer",
            field=models.EmailField(
                default="functioneelbeheerstz@rotterdam.nl", max_length=254
            ),
            preserve_default=False,
        ),
    ]
