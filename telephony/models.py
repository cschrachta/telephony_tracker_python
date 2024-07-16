import phonenumbers
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    e164_code = models.CharField(max_length=10, null=True, blank=True)
    iso2_code = models.CharField(max_length=5, blank=True)
    iso3_code = models.CharField(max_length=5, blank=True)
    numeric_code = models.IntegerField(blank=True, null=True)
    region = models.CharField(max_length=50, blank=True)
    subregion = models.CharField(max_length=50, blank=True)
    capital = models.CharField(max_length=100, blank=True)
    population = models.BigIntegerField(blank=True, null=True)
    area = models.FloatField(blank=True, null=True)
    currency_code = models.CharField(max_length=3, blank=True)
    currency_name = models.CharField(max_length=50, blank=True)
    language_code = models.CharField(max_length=2, blank=True)
    language_name = models.CharField(max_length=50, blank=True)
    flag_png_url = models.URLField(null=True, blank=True)
    flag_svg_url = models.URLField(null=True, blank=True)
    flag_alt_description = models.CharField(max_length=1024, null=True, blank=True)
    postal_code_format = models.CharField(max_length=255, blank=True, null=True)
    postal_code_regex = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name'] # Setting default to sort list alphabetically by country name

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200, blank=True, null=True)
    house_number = models.CharField(max_length=20)
    road = models.CharField(max_length=50)
    road_suffix = models.CharField(max_length=25, blank=True, null=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    state_abbreviation = models.CharField(max_length=5, blank=True, null=True)
    postcode = models.CharField(max_length=20)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    location_type = models.CharField(max_length=50, blank=True, null=True)
    verified_location = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('house_number', 'road', 'city', 'state_abbreviation', 'country'),)

    def __str__(self):
        return self.display_name or self.name or "Unnamed Location"

class StreetSuffix(models.Model):
    abbreviation = models.CharField(max_length=10, unique=True)
    full_name = models.CharField(max_length=50)

    def __str__(self):
        return self.abbreviation

class UsageType(models.Model):
    usage_type = models.CharField(max_length=50, unique=True, null=False)

    def __str__(self):
        return self.usage_type

class ServiceProvider(models.Model):
    provider_name = models.CharField(max_length=255, unique=True, null=False)
    website_url = models.URLField(max_length=255, blank=True)
    support_number = models.CharField(max_length=20, blank=True)
    contract_number = models.CharField(max_length=255, blank=True)
    contract_details = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.provider_name

class ServiceProviderRep(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    account_rep_name = models.CharField(max_length=255)
    account_rep_phone = models.CharField(max_length=20)
    account_rep_email = models.EmailField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account_rep_name

class SwitchType(models.Model):
    switch_type_name = models.CharField(max_length=100, unique=True, null=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.switch_type_name

class ConnectionType(models.Model):
    connection_type_name = models.CharField(max_length=100, unique=True, null=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.connection_type_name

class CircuitDetail(models.Model):
    circuit_number = models.CharField(max_length=50, unique=True, null=False)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    btn = models.CharField(max_length=20, blank=True)
    voice_channel_count = models.IntegerField(blank=True, null=True)
    connection_type = models.ForeignKey(ConnectionType, on_delete=models.CASCADE)
    switch_type = models.ForeignKey(SwitchType, on_delete=models.CASCADE, blank=True, null=True)
    contract_details = models.TextField(blank=True)
    ip_address = models.CharField(max_length=45, blank=True)
    supported_codecs = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.circuit_number

class PhoneNumberRange(models.Model):
    start_number = models.CharField(max_length=20)
    end_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    usage_type = models.ForeignKey(UsageType, on_delete=models.CASCADE)
    circuit = models.ForeignKey(CircuitDetail, on_delete=models.CASCADE, blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.start_number} - {self.end_number if self.end_number else self.start_number}"

    def clean(self):
        # Remove non-numeric characters
        cleaned_start_number = ''.join(filter(str.isdigit, self.start_number))
        cleaned_end_number = ''.join(filter(str.isdigit, self.end_number)) if self.end_number else None

        # Validate the start number
        e164_code = self.country.e164_code
        full_start_number = f"+{e164_code}{cleaned_start_number}"
        try:
            parsed_start_number = phonenumbers.parse(full_start_number, None)
            if not phonenumbers.is_valid_number(parsed_start_number):
                raise ValidationError('The start phone number is not valid.')
        except phonenumbers.NumberParseException:
            raise ValidationError('The start phone number could not be parsed.')

        # Validate the end number if it exists
        if cleaned_end_number:
            full_end_number = f"+{e164_code}{cleaned_end_number}"
            try:
                parsed_end_number = phonenumbers.parse(full_end_number, None)
                if not phonenumbers.is_valid_number(parsed_end_number):
                    raise ValidationError('The end phone number is not valid.')
            except phonenumbers.NumberParseException:
                raise ValidationError('The end phone number could not be parsed.')

            # Ensure the start number is less than the end number
            if int(cleaned_start_number) > int(cleaned_end_number):
                raise ValidationError('The start number must be less than the end number.')

        # Store the cleaned numbers in E164 format
        self.start_number = phonenumbers.format_number(parsed_start_number, phonenumbers.PhoneNumberFormat.E164)
        if cleaned_end_number:
            self.end_number = phonenumbers.format_number(parsed_end_number, phonenumbers.PhoneNumberFormat.E164)

    def save(self, *args, **kwargs):
        self.full_clean()  # This will call clean() method
        super().save(*args, **kwargs)
        self.create_phone_numbers()

    def create_phone_numbers(self):
            start_number_int = int(self.start_number.lstrip('+'))
            end_number_int = int(self.end_number.lstrip('+')) if self.end_number else start_number_int

            for number in range(start_number_int, end_number_int + 1):
                directory_number = f"+{self.country.e164_code}{number}"
                parsed_number = phonenumbers.parse(directory_number, None)

                phone_number, created = PhoneNumber.objects.update_or_create(
                directory_number=phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
                defaults={
                    'country': self.country,
                    'subscriber_number': parsed_number.national_number,
                    'service_location': self.location,
                    'usage_type': self.usage_type,
                    'service_provider': self.service_provider,
                    'phone_number_range': self,
                    'circuit': self.circuit,
                }
            )


class PhoneNumber(models.Model):
    directory_number = models.CharField(max_length=20, primary_key=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    subscriber_number = models.BigIntegerField()
    service_location = models.ForeignKey(Location, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    assigned_to = models.CharField(max_length=255, blank=True)
    usage_type = models.ForeignKey(UsageType, on_delete=models.CASCADE)
    last_used_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    number_format = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, blank=True)
    activation_date = models.DateField(blank=True, null=True)
    deactivation_date = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, blank=True, null=True)
    phone_number_range = models.ForeignKey(PhoneNumberRange, on_delete=models.CASCADE, blank=True, null=True)
    circuit = models.ForeignKey(CircuitDetail, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.directory_number)

    def clean(self):
        # Remove non-numeric characters
        cleaned_number = ''.join(filter(str.isdigit, self.directory_number))

        # Validate the phone number
        e164_code = self.country.e164_code
        full_number = f"+{e164_code}{cleaned_number}"
        try:
            parsed_number = phonenumbers.parse(full_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError('The phone number is not valid.')
        except phonenumbers.NumberParseException:
            raise ValidationError('The phone number could not be parsed.')

        # Store the cleaned number
        self.directory_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

    def save(self, *args, **kwargs):
        self.full_clean()  # This will call clean() method
        super().save(*args, **kwargs)

