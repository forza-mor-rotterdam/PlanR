# Generated by Django 3.2.16 on 2023-09-22 14:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authenticatie", "0002_profiel"),
    ]

    operations = [
        migrations.AddField(
            model_name="gebruiker",
            name="telefoonnummer",
            field=models.CharField(blank=True, max_length=17, null=True),
        ),
    ]
