# Generated by Django 3.2.16 on 2024-09-25 07:35

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_taaktypecategorie"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="standaardexterneomschrijving",
            options={
                "verbose_name": "Standaard tekst",
                "verbose_name_plural": "Standaard teksten",
            },
        ),
    ]
