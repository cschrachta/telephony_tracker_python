import phonenumbers, googlemaps, requests
from django.db import models
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.models import User
from .utils import validate_address
from django.db.models.signals import post_save
from django.dispatch import receiver


gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)

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
    
    
class LocationFunction(models.Model):
    function_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    function_code = models.CharField(max_length=1, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.function_code:
            self.function_code = self.generate_function_code()
        super().save(*args, **kwargs)

    def generate_function_code(self):
        # Implement logic to generate a unique function_code [0-9A-Z]
        # This could be based on the existing codes or a predefined set
        existing_codes = set(LocationFunction.objects.values_list('function_code', flat=True))
        available_codes = set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') - existing_codes
        if available_codes:
            return min(available_codes)  # or some other logic to pick the code
        else:
            raise ValueError("No available function codes left.")

    def __str__(self):
        return self.function_name


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
    location_function = models.ForeignKey(LocationFunction, on_delete=models.CASCADE, default=0)
    site_dial_code = models.IntegerField(blank=True, null=True)
    verified_location = models.BooleanField(default=False)
    formatted_address = models.CharField(max_length=255, blank=True)
    google_maps_place_id = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    site_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('house_number', 'road', 'city', 'state_abbreviation', 'country',)

    def __str__(self):
        return self.display_name or self.name or "Unnamed Location"
    
    def clean(self):
        # Construct the address for submission
        address = f"{self.house_number} {self.road}, {self.city}, {self.state}, {self.postcode}, {self.country.name}"
        api_key = settings.GOOGLE_API_KEY
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"

        response = requests.get(url)
        result = response.json()
        print(result)
        if result['status'] == 'OK' and result['results']:
            validated_address = result['results'][0]

            # Update the model fields with the validated data
            self.formatted_address = validated_address.get('formatted_address', '')
            self.google_maps_place_id = validated_address.get('place_id', '')
            self.house_number = next((component['long_name'] for component in validated_address['address_components'] if 'street_number' in component['types']), self.house_number)
            self.road = next((component['long_name'] for component in validated_address['address_components'] if 'route' in component['types']), self.road)
            self.city = next((component['long_name'] for component in validated_address['address_components'] if 'locality' in component['types']), self.city)
            self.state = next((component['short_name'] for component in validated_address['address_components'] if 'administrative_area_level_1' in component['types']), self.state)
            self.postcode = next((component['long_name'] for component in validated_address['address_components'] if 'postal_code' in component['types']), self.postcode)
            
            # Match country using ISO2 code, and if not found, try ISO3 code
            country_code_iso2 = next((component['short_name'] for component in validated_address['address_components'] if 'country' in component['types']), None)
            country_code_iso3 = next((component['long_name'] for component in validated_address['address_components'] if 'country' in component['types']), None)
            
            if country_code_iso2:
                try:
                    self.country = Country.objects.get(iso2_code=country_code_iso2)
                except Country.DoesNotExist:
                    if country_code_iso3:
                        try:
                            self.country = Country.objects.get(iso3_code=country_code_iso3)
                        except Country.DoesNotExist:
                            raise ValidationError(f"Country with ISO2 code {country_code_iso2} or ISO3 code {country_code_iso3} does not exist in the database.")
                    else:
                        raise ValidationError(f"Country with ISO2 code {country_code_iso2} does not exist in the database.")
            else:
                raise ValidationError("No country code found in the Google Maps API response.")

            self.latitude = validated_address['geometry']['location']['lat']
            self.longitude = validated_address['geometry']['location']['lng']

            # Set verified_location to True if the address validation was successful
            self.verified_location = True

        else:
            # If validation fails, raise an error or handle it appropriately
            raise ValidationError('Address could not be verified.')

        super().clean()

    def save(self, *args, **kwargs):
        if not self.site_id:  # Generate site_id if not already set
            self.site_id = self.generate_site_id()
        super().save(*args, **kwargs)

    def generate_site_id(self):
        country_code = self.country.iso2_code
        state_code = self.state_abbreviation[:2]  # or some other logic
        function_code = self.location_function.function_code
        site_id = f"{country_code}{state_code}{function_code}"
        return site_id

    def find_next_site_id(self, existing_ids):
        # Logic to find the next available ID...
        charset = '0123456789ABCDEF'
        existing_indices = [int(id[-5:], 16) for id in existing_ids]
        next_index = max(existing_indices) + 1 if existing_indices else 0
        return f"{next_index:05X}"  # Return as 5-character hexadecimal



class StreetSuffix(models.Model):
    abbreviation = models.CharField(max_length=10, unique=True)
    full_name = models.CharField(max_length=50)

    def __str__(self):
        return self.abbreviation

class UsageType(models.Model):
    USAGE_FOR_CHOICES = (
        ('PhoneNumber', 'Phone Number'),
        ('VoiceGateway', 'Voice Gateway'),
        ('AnalogGateway', 'Analog Gateway'),
        # Add more as needed
    )
    usage_type = models.CharField(max_length=50, unique=True, null=False, default='Phone')
    usage_for = models.CharField(max_length=50, choices=USAGE_FOR_CHOICES, default='PhoneNumber')

    def __str__(self):
        return f"{self.usage_type} ({self.get_usage_for_display()})"

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
        # Validate and format start number
        self.start_number = self._validate_and_format_number(self.start_number)
        
        # Validate and format end number if provided
        if self.end_number:
            self.end_number = self._validate_and_format_number(self.end_number)
            
            # Ensure the start number is less than the end number
            start_num_int = int(self.start_number.lstrip('+'))
            end_num_int = int(self.end_number.lstrip('+'))
            if start_num_int > end_num_int:
                raise ValidationError('The start number must be less than the end number.')
        else:
            self.end_number = self.start_number  # Treat as a single number range

    def _validate_and_format_number(self, number):
        """Validate and format a phone number."""
        cleaned_number = ''.join(filter(str.isdigit, number))
        full_number = f"+{self.country.e164_code}{cleaned_number}"
        try:
            parsed_number = phonenumbers.parse(full_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError(f'The phone number {number} is not valid.')
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValidationError(f'The phone number {number} could not be parsed.')

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
    id = models.AutoField(primary_key=True)  # Automatically added by Django if not specified
    directory_number = models.CharField(max_length=20, unique=True)
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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['directory_number'], name='unique_directory_number')
        ]

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



class HardwareDevice(models.Model):
    manufacturer = models.CharField(max_length=255, null=False)
    model = models.CharField(max_length=255, blank=True)
    serial_number = models.CharField(max_length=20, blank=True, unique=True)
    mac_address = models.CharField(max_length=255, blank=True, unique=True)
    service_location = models.ForeignKey(Location, on_delete=models.CASCADE)
    exists_in_phone_system = models.BooleanField(default=True)
    asset_tag = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    fqdn = models.CharField(max_length=255, null=False)
    firmware_version = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(blank=True, null=True)
    warranty_expiration = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Decommissioned', 'Decommissioned')], default='Active')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    last_maintenance_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True

class HardwarePhone(HardwareDevice):
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class HardwareGateway(HardwareDevice):

    def __str__(self):
        return self.name


class HardwareAnalogGateway(HardwareDevice):

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, unique=True)  # e.g., domain.com
    subscription_level = models.CharField(max_length=50, choices=[('free', 'Free'), ('premium', 'Premium')], default='free')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('user', 'User')])
    subscription_level = models.CharField(max_length=50, choices=[('free', 'Free'), ('premium', 'Premium')], default='free')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.company.name})"


class Subscription(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    level = models.CharField(max_length=50, choices=[('free', 'Free'), ('premium', 'Premium')], default='free')
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.company.name} - {self.level}"

