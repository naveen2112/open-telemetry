# Generated by Django 4.1.7 on 2023-08-23 17:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hubble", "0006_assessment_is_retry_needed_assessment_present_status_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assessment",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="assessment",
            name="score",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
