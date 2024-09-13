from django.core.management import BaseCommand, call_command
from telephony.models import UsageType, Location, ServiceProvider, ServiceProviderRep, Country

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        # List of usage types to seed
        usage_types = [
            ("Undesignated", "PhoneNumber"),
            ("Phone", "PhoneNumber"),
            ("Phone - Employee", "PhoneNumber"),
            ("Phone - Common Area", "PhoneNumber"),
            ("Phone - Public Space", "PhoneNumber"),
            ("Phone - Security", "PhoneNumber"),
            ("Phone - Delivery", "PhoneNumber"),
            ("Facsimile", "PhoneNumber"),
            ("Conference Bridge", "PhoneNumber"),
            ("Emergency Services", "PhoneNumber"),
            ("Alarm System", "PhoneNumber"),
            ("Elevator", "PhoneNumber"),
            ("Contact Center", "PhoneNumber"),
            ("Contact Center - IVR", "PhoneNumber"),
            ("Contact Center - Agent", "PhoneNumber"),
            ("Contact Center - Dialer", "PhoneNumber"),
            ("Auto Ringdown", "PhoneNumber"),
            ("Toll Free", "PhoneNumber"),
            ("Hotline", "PhoneNumber"),
            ("Voicemail", "PhoneNumber"),
            ("Voice Gateway", "VoiceGateway"),
            ("Analog Gateway", "AnalogGateway"),
        ]

        # Iterate through list and create each UsageType
        for usage_type, usage_for in usage_types:
            UsageType.objects.get_or_create(usage_type=usage_type, usage_for=usage_for)

        # Call the update_countries command to populate Country data from the internet
        call_command('update_countries')

        # Seed Location, ServiceProvider, and ServiceProviderRep data
        country, created = Country.objects.get_or_create(name="Test Country", code="TC")

        location, created = Location.objects.get_or_create(
            name="Sample Location", address="123 Sample St.", city="Sample City",
            state="Sample State", country=country, postal_code="12345",
            latitude=0.0000, longitude=0.0000
        )

        service_provider, created = ServiceProvider.objects.get_or_create(
            provider_name="Sample Provider", website="http://www.sampleprovider.com",
            support_number="+12345678900", notes="Sample service provider"
        )

        service_provider_rep, created = ServiceProviderRep.objects.get_or_create(
            rep_name="Sample Rep", rep_email="rep@sampleprovider.com",
            rep_phone="+12345678901", service_provider=service_provider,
            notes="Sample representative"
        )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))
        