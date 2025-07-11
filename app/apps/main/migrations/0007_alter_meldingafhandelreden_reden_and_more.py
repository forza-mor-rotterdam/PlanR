# Generated by Django 4.2.15 on 2025-06-10 17:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0006_meldingafhandelreden_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meldingafhandelreden",
            name="reden",
            field=models.CharField(
                choices=[
                    ("reeds_ingepland", "Reeds ingepland"),
                    ("niet_nu", "Niet nu"),
                    ("niet_voor_ons", "Niet voor ons"),
                    ("doen_we_niet", "Doen we niet"),
                    ("onduidelijk", "Onduidelijk"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="standaardexterneomschrijving",
            name="reden",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="standaard_externe_omschrijvingen_voor_melding_afhandelreden",
                to="main.meldingafhandelreden",
            ),
        ),
    ]
