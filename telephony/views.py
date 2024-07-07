import googlemaps
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Location, ServiceProvider, CircuitDetail, PhoneNumber, Country
from .forms import CircuitDetailForm, LocationForm, SearchForm, PhoneNumberForm, CountryForm

logger = logging.getLogger(__name__)

# Home View
def index(request):
    return render(request, 'telephony/index.html')

# Location Views
def locations(request):
    if request.method == 'POST':
        form = LocationForm(request.POST or None)
        if form.is_valid():
            success, message = verify_and_save_location(form)
            if success:
                messages.success(request, message)
                return redirect('locations')
            else:
                messages.error(request, message)
    else:
        form = LocationForm()
    return render(request, 'telephony/locations.html', {'form': form, 'locations': Location.objects.all()})

def verify_location(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    success, message = verify_and_save_location(LocationForm(instance=location))
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('locations')

def delete_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    if request.method == 'POST':
        location.delete()
        messages.success(request, 'Location deleted successfully!')
        return redirect('locations')
    return render(request, 'telephony/confirm_delete.html', {'location': location})

@require_http_methods(["GET"])
def get_location(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    data = {
        'name': location.name,
        'display_name': location.display_name,
        'house_number': location.house_number,
        'road': location.road,
        'road_suffix': location.road_suffix,
        'city': location.city,
        'state_abbreviation': location.state_abbreviation,
        'postcode': location.postcode,
        'country': location.country.name,
        'notes': location.notes,
    }
    return JsonResponse(data)

def verify_and_save_location(form):
    address = form.cleaned_data['address']
    gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
    geocode_result = gmaps.geocode(address)

    if not geocode_result:
        return False, 'Invalid address'

    geo_location = geocode_result[0]['geometry']['location']
    address_components = geocode_result[0]['address_components']

    components = {
        'street_number': 'short_name',
        'route': 'long_name',
        'locality': 'long_name',
        'administrative_area_level_1': 'long_name',
        'administrative_area_level_2': 'short_name',
        'postal_code': 'short_name',
        'country': 'short_name',
    }
    extracted_address = {}
    for component in address_components:
        address_type = component['types'][0]
        if address_type in components:
            extracted_address[address_type] = component[components[address_type]]
        if address_type == 'administrative_area_level_1':
            form.cleaned_data['state_abbreviation'] = component['short_name']
            form.cleaned_data['state'] = component['long_name']

    form.cleaned_data['latitude'] = geo_location['lat']
    form.cleaned_data['longitude'] = geo_location['lng']
    form.cleaned_data['verified_location'] = True
    form.cleaned_data['house_number'] = extracted_address.get('street_number', '')
    form.cleaned_data['road'] = extracted_address.get('route', '')
    form.cleaned_data['city'] = extracted_address.get('locality', '')
    form.cleaned_data['postcode'] = extracted_address.get('postal_code', '')

    country_code = extracted_address.get('country', '')
    if country_code:
        try:
            form.cleaned_data['country'] = Country.objects.get(iso2_code=country_code)
        except Country.DoesNotExist:
            try:
                form.cleaned_data['country'] = Country.objects.get(iso3_code=country_code)
            except Country.DoesNotExist:
                try:
                    form.cleaned_data['country'] = Country.objects.get(name=country_code)
                except Country.DoesNotExist:
                    return False, f'Country with ISO code "{country_code}" does not exist in the database'

    location = form.save(commit=False)
    timezone_result = gmaps.timezone((location.latitude, location.longitude))
    location.timezone = timezone_result['timeZoneId']
    location.save()

    logger.debug(f'Country code received: {country_code}')
    logger.debug(f'Extracted address: {extracted_address}')

    return True, 'Location added successfully!'

# Service Provider Views
def service_providers(request):
    service_providers = ServiceProvider.objects.all()
    return render(request, 'telephony/service_provider.html', {'service_providers': service_providers})

# Circuit Views
def circuits(request):
    circuits = CircuitDetail.objects.all()
    return render(request, 'telephony/circuits.html', {'circuits': circuits})

def add_circuit_detail(request):
    if request.method == 'POST':
        form = CircuitDetailForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = CircuitDetailForm()
    return render(request, 'add_circuit_detail.html', {'form': form})

# Phone Number Views
def phone_numbers(request):
    form = SearchForm(request.GET or None)
    phone_numbers = PhoneNumber.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            phone_numbers = phone_numbers.filter(directory_number__icontains=query)

    sort_by = request.GET.get('sort_by', 'directory_number')
    order = request.GET.get('order', 'asc')
    phone_numbers = phone_numbers.order_by(f"{'-' if order == 'desc' else ''}{sort_by}")

    return render(request, 'telephony/phone_numbers.html', {
        'phone_numbers': phone_numbers,
        'sort_by': sort_by,
        'order': order,
        'form': form,
    })

# Country Views
def country_list(request):
    countries = Country.objects.all()
    return render(request, 'telephony/country_list.html', {'countries': countries})