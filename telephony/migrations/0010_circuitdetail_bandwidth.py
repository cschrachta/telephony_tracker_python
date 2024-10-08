# Generated by Django 5.1.1 on 2024-09-26 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telephony', '0009_alter_hardwareanaloggateway_mac_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuitdetail',
            name='bandwidth',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Bandwidth in Mbps or Gbps', max_digits=10, null=True),
        ),
    ]
