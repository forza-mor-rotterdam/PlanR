# Generated by Django 4.2.15 on 2024-10-14 12:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NieuweMeldingAantallen",
            fields=[],
            options={
                "verbose_name": "Nieuwe melding aantallen",
                "verbose_name_plural": "Nieuwe melding aantallen",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dashboard.tijdsvak",),
        ),
        migrations.CreateModel(
            name="NieuweSignaalAantallen",
            fields=[],
            options={
                "verbose_name": "Nieuwe signaal aantallen",
                "verbose_name_plural": "Nieuwe signaal aantallen",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dashboard.tijdsvak",),
        ),
        migrations.CreateModel(
            name="NieuweTaakopdrachten",
            fields=[],
            options={
                "verbose_name": "Nieuwe taakopdrachten",
                "verbose_name_plural": "Nieuwe taakopdrachten",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dashboard.tijdsvak",),
        ),
        migrations.CreateModel(
            name="StatusVeranderingDuurMeldingen",
            fields=[],
            options={
                "verbose_name": "Status verandering duur voor meldingen",
                "verbose_name_plural": "Status verandering duur voor meldingen",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dashboard.tijdsvak",),
        ),
        migrations.CreateModel(
            name="TaakopdrachtDoorlooptijden",
            fields=[],
            options={
                "verbose_name": "Taakopdracht doorlooptijden",
                "verbose_name_plural": "Taakopdracht doorlooptijden",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dashboard.tijdsvak",),
        ),
        migrations.CreateModel(
            name="TaaktypeAantallenPerMelding",
            fields=[],
            options={
                "verbose_name": "Taaktype aantallen per melding",
                "verbose_name_plural": "Taaktype aantallen per melding",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dashboard.tijdsvak",),
        ),
        migrations.AlterModelOptions(
            name="doorlooptijdenafgehandeldemeldingen",
            options={
                "verbose_name": "Doorlooptijden afgehandelde meldingen",
                "verbose_name_plural": "Doorlooptijden afgehandelde meldingen",
            },
        ),
        migrations.AlterModelOptions(
            name="tijdsvak",
            options={
                "ordering": ["start_datumtijd"],
                "verbose_name": "Tijdsvak",
                "verbose_name_plural": "Tijdsvakken",
            },
        ),
        migrations.AlterField(
            model_name="databron",
            name="brontype",
            field=models.CharField(
                choices=[
                    (
                        "doorlooptijden_afgehandelde_meldingen",
                        "Doorlooptijden afgehandelde meldingen",
                    ),
                    (
                        "status_verandering_duur_meldingen",
                        "Status verandering duur voor meldingen",
                    ),
                    ("nieuwe_melding_aantallen", "Nieuwe melding aantallen"),
                    ("nieuwe_signaal_aantallen", "Nieuwe signaal aantallen"),
                    ("nieuwe_taakopdrachten", "Nieuwe taakopdrachten"),
                    (
                        "taaktype_aantallen_per_melding",
                        "Taaktype aantallen per melding",
                    ),
                    ("taakopdracht_doorlooptijden", "Taakopdracht doorlooptijden"),
                ],
                max_length=100,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="databron",
            name="url",
            field=models.URLField(),
        ),
    ]
