# Generated by Django 5.1.1 on 2024-09-13 14:24

import django.db.models.deletion
import telephony.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telephony', '0007_alter_circuitdetail_connection_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circuitdetail',
            name='provider',
            field=models.ForeignKey(default=telephony.models.get_default_service_provider, on_delete=django.db.models.deletion.SET_DEFAULT, to='telephony.serviceprovider'),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
