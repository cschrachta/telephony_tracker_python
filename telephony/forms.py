import requests
import googlemaps
from django import forms
from .models import CircuitDetail, ConnectionType, Location, PhoneNumberRange, PhoneNumber, Country
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
    address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'id': 'id_address', 'placeholder': 'Enter Address:'}))

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            address = f'{self.instance.house_number} {self.instance.road}, {self.instance.city}, {self.instance.state_abbreviation} {self.instance.postcode}, {self.instance.country.iso2_code}'
            self.fields['address'].initial = address

    def clean_address(self):
        address = self.cleaned_data['address']
        gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
        geocode_result = gmaps.geocode(address)

        if not geocode_result:
            raise forms.ValidationError('Invalid address')

        # Extract address components from the geocode result
        geo_location = geocode_result[0]['geometry']['location']
        address_components = geocode_result[0]['address_components']
        
        components = {
            'street_number': 'short_name',
            'route': 'long_name',
            'locality': 'long_name',
            'administrative_area_level_1': 'short_name',
            'postal_code': 'short_name',
            'country': 'short_name',
        }
        extracted_address = {}
        for component in address_components:
            address_type = component['types'][0]
            if address_type in components:
                extracted_address[address_type] = component[components[address_type]]
        
        self.cleaned_data['latitude'] = geo_location['lat']
        self.cleaned_data['longitude'] = geo_location['lng']
        self.cleaned_data['verified_location'] = True  # Set verified_location to True if coordinates are available
        # Set the validated address components to the form fields
        self.cleaned_data['house_number'] = extracted_address.get('street_number', '')
        self.cleaned_data['road'] = extracted_address.get('route', '')
        self.cleaned_data['city'] = extracted_address.get('locality', '')
        self.cleaned_data['state_abbreviation'] = extracted_address.get('administrative_area_level_1', '')
        self.cleaned_data['postcode'] = extracted_address.get('postal_code', '')

        for component in address_components:
            if 'locality' in component['types']:
                self.cleaned_data['city'] = component['long_name']
            if 'administrative_area_level_2' in component['types']:
                self.cleaned_data['county'] = component['long_name']
            if 'country' in component['types']:
                country_code = component['short_name']
                try:
                    country_instance = Country.objects.get(iso2_code=country_code)
                    self.cleaned_data['country'] = country_instance
                except Country.DoesNotExist:
                    raise forms.ValidationError(f'Country with ISO code "{country_code}" does not exist in the database')

        return address

    def save(self, commit=True):
        location = super().save(commit=False)
        location.house_number = self.cleaned_data.get('house_number', '')
        location.road = self.cleaned_data.get('road', '')
        location.city = self.cleaned_data.get('city', '')
        location.state = self.cleaned_data.get('state', '')
        location.state_abbreviation = self.cleaned_data.get('state_abbreviation', '')
        location.postcode = self.cleaned_data.get('postcode', '')
        location.country = self.cleaned_data.get('country', None)
        location.latitude = self.cleaned_data.get('latitude', None)
        location.longitude = self.cleaned_data.get('longitude', None)
        location.county = self.cleaned_data.get('county', '')

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
            'state',
            'state_abbreviation',
            'postcode',
            'country',
            'timezone',
            'contact_person',
            'contact_email',
            'contact_phone',
            'location_type',
            'notes',
        ]
        widgets = {
            'house_number': forms.HiddenInput(),
            'road': forms.HiddenInput(),
            'road_suffix': forms.HiddenInput(),
            'city': forms.HiddenInput(),
            'state': forms.HiddenInput(),
            'state_abbreviation': forms.HiddenInput(),
            'postcode': forms.HiddenInput(),
            'country': forms.HiddenInput(),
            'timezone': forms.HiddenInput(),
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
        fields = ['name', 'e164_code', 'region', 'subregion', 'capital']


