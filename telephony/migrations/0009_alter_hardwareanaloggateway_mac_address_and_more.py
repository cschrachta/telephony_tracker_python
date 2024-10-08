# Generated by Django 5.1.1 on 2024-09-14 18:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telephony', '0008_alter_circuitdetail_provider_alter_location_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hardwareanaloggateway',
            name='mac_address',
            field=models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(message='Enter a valid MAC address.', regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')]),
        ),
        migrations.AlterField(
            model_name='hardwaregateway',
            name='mac_address',
            field=models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(message='Enter a valid MAC address.', regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')]),
        ),
        migrations.AlterField(
            model_name='hardwarephone',
            name='mac_address',
            field=models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(message='Enter a valid MAC address.', regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')]),
        ),
    ]
