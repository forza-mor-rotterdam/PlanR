from django.db import migrations, models


def truncate_standaardexterneomschrijving_tekst(apps, schema_editor):
    StandaardExterneOmschrijving = apps.get_model(
        "main", "StandaardExterneOmschrijving"
    )
    for record in StandaardExterneOmschrijving.objects.all():
        record.tekst = record.tekst[:1000]
        record.save()


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_alter_standaardexterneomschrijving_tekst"),
    ]

    operations = [
        migrations.RunPython(truncate_standaardexterneomschrijving_tekst),
        migrations.AlterField(
            model_name="standaardexterneomschrijving",
            name="tekst",
            field=models.CharField(max_length=1000),
        ),
    ]
