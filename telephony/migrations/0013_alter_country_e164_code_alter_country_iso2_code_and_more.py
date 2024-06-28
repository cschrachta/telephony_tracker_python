# Generated by Django 5.0.6 on 2024-06-22 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telephony', '0012_alter_country_flag_alt_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='e164_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='iso2_code',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='country',
            name='iso3_code',
            field=models.CharField(blank=True, max_length=5),
        ),
    ]
