import googlemaps
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.management import call_command
from django.db.models import Q
from .models import Location, ServiceProvider, CircuitDetail, PhoneNumber, Country
from .forms import CircuitDetailForm, LocationForm, SearchForm, PhoneNumberForm, CountryForm

# Create your views here.

def index(request):
    return render(request, 'telephony/index.html')

def locations(request):
    if request.method == 'POST':
        form = LocationForm(request.POST or None)
        if form.is_valid():
            location = form.save(commit=False)
            location.verified_location = True  # Set to true if Google verification is successful
            location.save()
            return redirect('locations')
    else:
        form = LocationForm()

    locations = Location.objects.all()
    return render(request, 'telephony/locations.html', {'form': form, 'locations': locations})

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

@require_http_methods(["GET"])
def verify_location_view(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    # Call the Google API to verify the address and update the location
    success = verify_address_with_google(location)
    if success:
        location.verified_location = True
        location.save()
    return JsonResponse({'success': success})

@require_http_methods(["DELETE"])
def delete_location(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    location.delete()
    return JsonResponse({'success': True})

def verify_address_with_google(location):
    # Implement the actual verification logic with Google API
    # Return True if the address is verified successfully, False otherwise
    return True


def service_providers(request):
    service_providers = ServiceProvider.objects.all()
    return render(request, 'telephony/service_provider.html', {'service_providers': service_providers})

def circuits(request):
    circuits = CircuitDetail.objects.all()
    return render(request, 'telephony/circuits.html', {'circuits': circuits})

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
        'form': form,  # Pass the form to the template
    })

def add_circuit_detail(request):
    if request.method == 'POST':
        form = CircuitDetailForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = CircuitDetailForm()
    return render(request, 'add_circuit_detail.html', {'form': form})

def country_list(request):
    countries = Country.objects.all()
    #sorted_countries = sorted(countries, key=lambda x: (x.name != "United States", x.name))
    return render(request, 'telephony/country_list.html', {'countries': countries})

def verify_location(request, location_id):
    location = get_object_or_404(Location, pk=location_id)

    # Construct the full address from the location record
    address = f'{location.house_number} {location.road}, {location.city}, {location.state_abbreviation} {location.postcode}, {location.country.iso2_code}'

    # Use Google Maps API to validate the address
    gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
    geocode_result = gmaps.geocode(address)

    if not geocode_result:
        messages.error(request, 'Invalid address')
        return redirect('locations')

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

    # Update the location record with the validated address components
    location.house_number = extracted_address.get('street_number', '')
    location.road = extracted_address.get('route', '')
    location.city = extracted_address.get('locality', '')
    location.state = extracted_address.get('administrative_area_level_1_full', '')
    location.state_abbreviation = extracted_address.get('administrative_area_level_1', '')
    location.postcode = extracted_address.get('postal_code', '')

    # Getting the country by ISO2 code
    country_code = extracted_address.get('country', '')
    if country_code:
        try:
            location.country = Country.objects.get(iso2_code=country_code)
        except Country.DoesNotExist:
            messages.error(request, f'Country with ISO code "{country_code}" does not exist in the database')
            return redirect('locations')

    if geocode_result:
        geo_location = geocode_result[0]['geometry']['location']
        location.latitude = geo_location['lat']
        location.longitude = geo_location['lng']
        location.verified_location = True
        
        timezone_result = gmaps.timezone((location.latitude, location.longitude))
        location.timezone = timezone_result['timeZoneId']
        location.save()
        
        messages.success(request, 'Location verified successfully!')
    else:
        messages.error(request, 'Could not verify location.')
    
    return redirect('locations')

def delete_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    if request.method == 'POST':
        location.delete()
        messages.success(request, 'Location deleted successfully!')
        return redirect('locations')
    return render(request, 'telephony/confirm_delete.html', {'location': location})

def location_list(request):
    locations = Location.objects.all()
    return render(request, 'telephony/locations.html', {'locations': locations})

def verify_location_view(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    verify_location(location)
    return HttpResponseRedirect('/locations/')  # Redirect to the location list

def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST or None)
        if form.is_valid():
            address = form.cleaned_data['address']
            api_key = settings.GOOGLE_API_KEY
            url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
            response = requests.get(url)
            data = response.json()
            if data['status'] == 'OK':
                # Extract address components and validate
                # Populate other form fields or handle validation as needed
                form.save()
                messages.success(request, 'Location added successfully!')
                return redirect('location_list')
            else:
                messages.error(request, 'Invalid address.')
    else:
        form = LocationForm()
    return render(request, 'telephony/add_location.html', {'form': form})