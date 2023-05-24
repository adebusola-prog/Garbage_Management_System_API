# Generated by Django 4.2.1 on 2023-05-24 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_initial"),
        ("garbage_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collectionplan",
            name="garbage_collector",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="my_plans",
                to="accounts.garbagecollector",
            ),
        ),
        migrations.AlterField(
            model_name="collectionrequest",
            name="location",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="garbage_app.location",
            ),
        ),
        migrations.AlterField(
            model_name="collectionrequest",
            name="plan",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="garbage_app.collectionplan",
            ),
        ),
    ]