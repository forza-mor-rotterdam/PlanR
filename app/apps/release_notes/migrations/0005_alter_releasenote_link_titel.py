# Generated by Django 4.2.15 on 2024-11-13 13:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("release_notes", "0004_releasenote_link_titel_releasenote_link_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="releasenote",
            name="link_titel",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
