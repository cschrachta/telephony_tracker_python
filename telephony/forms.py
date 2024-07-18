import requests
import googlemaps
from django import forms
from .models import CircuitDetail, ConnectionType, Location, PhoneNumberRange, PhoneNumber, Country, ServiceProvider
from django.conf import settings

class CircuitDetailForm(forms.ModelForm):
    class Meta:
        model = CircuitDetail
        fields = [
            'circuit_number', 'provider', 'location', 'btn', 'voice_channel_count',
            'connection_type', 'contract_details', 'ip_address', 'supported_codecs'
        ]
        widgets = {
            'connection_type': forms.Select(attrs={'id': 'connectionType'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ip_address'].widget.attrs.update({'class': 'hidden'})
        self.fields['supported_codecs'].widget.attrs.update({'class': 'hidden'})


class LocationForm(forms.ModelForm):
    # Remove the address field
    # address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'id': 'id_address', 'placeholder': 'Enter Address:'}))

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            formatted_address = f'{self.instance.house_number} {self.instance.road}, {self.instance.city}, {self.instance.state_abbreviation} {self.instance.postcode}, {self.instance.country.iso2_code}'
            # self.fields['address'].initial = formatted_address

    def clean(self):
        cleaned_data = super().clean()

        # Construct the address for Google geocoding
        submitted_address = f"{cleaned_data.get('house_number')} {cleaned_data.get('road')}, {cleaned_data.get('city')}, {cleaned_data.get('state_abbreviation')} {cleaned_data.get('postcode')}, {cleaned_data.get('country').name}"

        gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
        geocode_result = gmaps.geocode(submitted_address)

        if not geocode_result:
            raise forms.ValidationError('Invalid address')

        # Extract address components from the geocode result
        address_components = geocode_result[0]['address_components']
        geo_location = geocode_result[0]['geometry']['location']
        # google_formatted_address = geocode_result[0]['submitted_address']
        
        components = {
            'street_number': 'short_name',
            'route': 'long_name',
            'locality': 'long_name',
            'administrative_area_level_1': 'short_name',
            'administrative_area_level_2': 'long_name',
            'postal_code': 'short_name',
            'country': 'short_name',
        }

        extracted_address = {}
        for component in address_components:
            address_type = component['types'][0]
            if address_type in components:
                extracted_address[address_type] = component[components[address_type]]
            if address_type == 'administrative_area_level_1':
                cleaned_data['state_abbreviation'] = component['short_name']
                cleaned_data['state'] = component['long_name']
            if address_type == 'administrative_area_level_2':
                cleaned_data['county'] = component['long_name']
        cleaned_data['house_number'] = extracted_address.get('street_number', '')
        cleaned_data['road'] = extracted_address.get('route', '')
        cleaned_data['city'] = extracted_address.get('locality', '')
        cleaned_data['postcode'] = extracted_address.get('postal_code', '')
        country_code = extracted_address.get('country', '') 
        if country_code:
            try:
                country_instance = Country.objects.get(iso2_code=country_code)
            except Country.DoesNotExist:
                try:
                    country_instance = Country.objects.get(iso3_code=country_code)
                except Country.DoesNotExist:
                    try:
                        country_instance = Country.objects.get(name=country_code)
                    except Country.DoesNotExist:
                        raise forms.ValidationError(f'Country with code "{country_code}" does not exist in the database')
            cleaned_data['country'] = country_instance

        cleaned_data['longitude'] = geo_location['lng']
        cleaned_data['latitude'] = geo_location['lat']
        
        cleaned_data['verified_location'] = True  # Set verified_location to True if coordinates are available
        
        return cleaned_data

    def save(self, commit=True):
        location = super().save(commit=False)
        location.name = self.cleaned_data.get('name',f'site {location.id}')
        location.display_name = self.cleaned_data.get('display_name', '')
        location.house_number = self.cleaned_data.get('house_number', '')
        location.road = self.cleaned_data.get('road', '')
        location.road_suffix = self.cleaned_data.get('road_suffix', '')
        location.city = self.cleaned_data.get('city', '')
        location.county = self.cleaned_data.get('county', '')
        location.state = self.cleaned_data.get('state', '')
        location.state_abbreviation = self.cleaned_data.get('state_abbreviation', '')
        location.postcode = self.cleaned_data.get('postcode', '')
        location.country = self.cleaned_data.get('country', None)
        location.latitude = self.cleaned_data.get('latitude', None)
        location.longitude = self.cleaned_data.get('longitude', None)
        location.contact_person = self.cleaned_data.get('contact_person', '')
        location.contact_email = self.cleaned_data.get('contact_email', '')
        location.contact_phone = self.cleaned_data.get('contact_phone', '')
        location.location_type = self.cleaned_data.get('location_type', '')
        location.notes = self.cleaned_data.get('notes', '')

        gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
        timezone_result = gmaps.timezone((location.latitude, location.longitude))
        location.timezone = timezone_result['timeZoneId']
        if commit:
            location.save()
        return location

    class Meta:
        model = Location
        fields = [
            'name',
            'display_name',
            'house_number',
            'road',
            'road_suffix',
            'city',
            'county',
            'state',
            'state_abbreviation',
            'postcode',
            'country',
            'latitude',
            'longitude',
            'timezone',
            'contact_person',
            'contact_email',
            'contact_phone',
            'location_type',
            'notes',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Site Referred to as'}),
            'display_name': forms.TextInput(attrs={'placeholder': 'Site Reference Name'}),
            'house_number': forms.TextInput(attrs={'placeholder': '123'}),
            'road': forms.TextInput(attrs={'placeholder': 'Main, 1st, etc...'}),
            'road_suffix': forms.TextInput(attrs={'placeholder': 'St, Ave, etc.'}),
            'city': forms.TextInput(attrs={'placeholder': 'City Name'}),
            'county': forms.TextInput(attrs={'placeholder': 'County Name'}),
            'state': forms.TextInput(attrs={'placeholder': 'California'}),
            'state_abbreviation': forms.TextInput(attrs={'placeholder': 'CA'}),
            'postcode': forms.TextInput(attrs={'placeholder': '12345'}),
            'country': forms.Select(attrs={'placeholder': 'Choose from list'}),
            'latitude': forms.TextInput(attrs={'placeholder': 'Latitude'}),
            'longitude': forms.TextInput(attrs={'placeholder': 'Longitude'}),
            'contact_person': forms.TextInput(attrs={'placeholder': 'Main Support Person'}),
            'contact_email': forms.TextInput(attrs={'placeholder': 'Main Support Email'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'Main Contacts Number'}),
            'location_type': forms.TextInput(attrs={'placeholder': 'Admin, Manufacturing, etc...'}),
            'timezone': forms.TextInput(attrs={'placeholder': 'GMT'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Additional notes here...'}),
        }


class PhoneNumberRangeForm(forms.ModelForm):
    class Meta:
        model = PhoneNumberRange
        fields = ['start_number', 'end_number', 'country', 'location', 'usage_type', 'notes']


class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        fields = ['directory_number', 'country', 'service_provider', 'service_location', 'usage_type', 'notes']


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name', 'iso2_code', 'iso3_code', 'e164_code', 'region', 'subregion', 'capital']


class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = [
            'provider_name',
            'website_url',
            'support_number',
            'contract_number',
            'contract_details',
            'notes'
        ]
        widgets = {
            'provider_name': forms.TextInput(attrs={'placeholder': 'Provider Name'}),
            'website_url': forms.URLInput(attrs={'placeholder': 'https://www.provider.com'}),
            'support_number': forms.TextInput(attrs={'placeholder': 'Support: +18005551212'}),
            'contract_number': forms.TextInput(attrs={'placeholder': 'Contract ID'}),
            'contract_details': forms.Textarea(attrs={'placeholder': 'Contract Details'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Notes'}),
        }