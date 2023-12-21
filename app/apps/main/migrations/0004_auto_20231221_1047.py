from django.db import migrations


def create_default_standaard_omschrijving(apps, schema_editor):
    StandaardExterneOmschrijving = apps.get_model(
        "main", "StandaardExterneOmschrijving"
    )

    if not StandaardExterneOmschrijving.objects.filter(
        titel="Standaard afhandelreden"
    ).exists():
        StandaardExterneOmschrijving.objects.create(
            titel="Standaard afhandelreden",
            tekst="Deze melding is behandeld. Bedankt voor uw inzet om Rotterdam schoon, heel en veilig te houden.",
        )


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0003_alter_standaardexterneomschrijving_tekst"),
    ]

    operations = [
        migrations.RunPython(create_default_standaard_omschrijving),
    ]
