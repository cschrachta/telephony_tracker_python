from django.core.management.base import BaseCommand
from telephony.models import UsageType

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        UsageType.objects.get_or_create(usage_type="Phone", usage_for="PhoneNumber")
        UsageType.objects.get_or_create(usage_type="Voice Gateway", usage_for="VoiceGateway")
        UsageType.objects.get_or_create(usage_type="Analog Gateway", usage_for="AnalogGateway")
        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))