# Generated by Django 4.2.15 on 2025-01-08 09:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authenticatie", "0004_alter_gebruiker_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="gebruiker",
            name="verwijderd_op",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
