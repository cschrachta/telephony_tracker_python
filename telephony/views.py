import googlemaps
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Location, ServiceProvider, CircuitDetail, PhoneNumber, Country
from .forms import CircuitDetailForm, LocationForm, SearchForm, PhoneNumberForm, CountryForm, ServiceProviderForm
#from .utils import verify_and_save_location

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

# def verify_location(request, id):
#     location = get_object_or_404(Location, id=id)
#     if request.method == 'POST':
#         form = LocationForm(request.POST, instance=location)
#         if form.is_valid():
#             success, message = verify_and_save_location(form)
#             return JsonResponse({'success': success, 'message': message})
#         else:
#             return JsonResponse({'success': False, 'message': 'Form data is not valid'})
#     return JsonResponse({'success': False, 'message': 'Invalid request method'})

def verify_location(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    if request.method == "POST":
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            success, message = verify_and_save_location(form)
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect('locations')
    else:
        form = LocationForm(instance=location)
    return render(request, 'telephony/locations.html', {'form': form, 'locations': Location.objects.all()})

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
        'county': location.county,
        'state': location.state,
        'state_abbreviation': location.state_abbreviation,
        'postcode': location.postcode,
        'country': location.country.id,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'timezone': location.timezone,
        'contact_person': location.contact_person,
        'contact_email': location.contact_email,
        'contact_phone': location.contact_phone,
        'location_type': location.location_type,
        'notes': location.notes,
    }
    return JsonResponse(data)

def verify_and_save_location(form):
    if not form.is_valid():
        return False, 'Form is not valid'

    cleaned_data = form.cleaned_data
    house_number = cleaned_data.get('house_number', '')
    road = cleaned_data.get('road', '')
    city = cleaned_data.get('city', '')
    state_abbreviation = cleaned_data.get('state_abbreviation', '')
    postcode = cleaned_data.get('postcode', '')
    country = cleaned_data.get('country', None)
    contact_person = cleaned_data.get('contact_person', '')
    contact_email = cleaned_data.get('contact_email', '')
    contact_phone = cleaned_data.get('contact_phone', '')
    location_type = cleaned_data.get('location_type', '')
    notes = cleaned_data.get('notes', '')

    # Check for duplicates
    # if Location.objects.filter(house_number, road, city, state_abbreviation, postcode, country).exists():
    #     return False, 'A location with this address already exists.'

    try:
        location = Location.objects.get(
            house_number=house_number, 
            road=road, 
            city=city, 
            state_abbreviation=state_abbreviation, 
            postcode=postcode, 
            country=country,
        )
    except Location.DoesNotExist:
        location = None
    
    address = f"{house_number} {road}, {city}, {state_abbreviation} {postcode}, {country.name}"

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
            form.cleaned_data['state_abbreviation'] = component['short_name']
            form.cleaned_data['state'] = component['long_name']
        if address_type == 'administrative_area_level_2':
            form.cleaned_data['county'] = component['long_name']

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

    form.cleaned_data['latitude'] = geo_location['lat']
    form.cleaned_data['longitude'] = geo_location['lng']
    form.cleaned_data['verified_location'] = True

    location = form.save(commit=False)
    timezone_result = gmaps.timezone((location.latitude, location.longitude))
    location.timezone = timezone_result['timeZoneId']
    location.verified_location = True
    location.save()

    # logger.debug(f'Country code received: {country_code}')
    # logger.debug(f'Extracted address: {extracted_address}')

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


#Country Views
def country_list(request):
    countries = Country.objects.all()
    return render(request, 'telephony/country_list.html', {'countries': countries})


def service_provider(request):
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_provider')  # Replace with the actual name of your list view
    else:
        form = ServiceProviderForm()
    
    service_providers = ServiceProvider.objects.all()
    return render(request, 'telephony/service_provider.html', {'form': form, 'service_providers': service_providers})


def add_service_provider(request):
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('telephony/service_provider')  # Replace with the actual name of your list view
    else:
        form = ServiceProviderForm()
    
    service_providers = ServiceProvider.objects.all()
    return render(request, 'telephony/add_service_provider.html', {'form': form, 'service_providers': service_providers})

def delete_service_provider(request, provider_id):
    service_provider = get_object_or_404(ServiceProvider, id=provider_id)
    service_provider.delete()
    return redirect('telephony:service_provider')  # Adjust this to the correct URL name

def get_service_provider(request, provider_id):
    service_provider = get_object_or_404(ServiceProvider, id=provider_id)
    data = {
        'provider_name': service_provider.provider_name,
        'support_number': service_provider.support_number,
        'contract_number': service_provider.contract_number,
        'contract_details': service_provider.contract_details,
        'website_url': service_provider.website_url,
        'notes': service_provider.notes,
    }
    return JsonResponse(data)