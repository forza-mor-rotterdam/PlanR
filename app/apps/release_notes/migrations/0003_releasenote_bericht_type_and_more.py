# Generated by Django 4.2.15 on 2024-11-04 15:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("release_notes", "0002_alter_releasenote_beschrijving"),
    ]

    operations = [
        migrations.AddField(
            model_name="releasenote",
            name="bericht_type",
            field=models.CharField(
                choices=[
                    ("release_note", "Release note"),
                    ("notificatie", "Notificatie"),
                ],
                default="release_note",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="releasenote",
            name="einde_publicatie_datum",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="releasenote",
            name="korte_beschrijving",
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name="releasenote",
            name="notificatie_niveau",
            field=models.CharField(
                choices=[
                    ("info", "Informatief"),
                    ("warning", "Waarschuwing"),
                    ("error", "Foutmelding"),
                ],
                default="info",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="releasenote",
            name="notificatie_type",
            field=models.CharField(
                choices=[("snack", "Snack"), ("toast", "Toast")],
                default="snack",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="releasenote",
            name="toast_miliseconden_zichtbaar",
            field=models.PositiveSmallIntegerField(default=6000),
        ),
        migrations.AddField(
            model_name="releasenote",
            name="verwijderbaar",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="releasenote",
            name="beschrijving",
            field=models.TextField(blank=True, max_length=5000, null=True),
        ),
    ]