from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.db.models import Q
from .models import Location, ServiceProvider, CircuitDetail, PhoneNumber, Country
from .forms import CircuitDetailForm, LocationForm, SearchForm, PhoneNumberForm, CountryForm

# Create your views here.

def index(request):
    return render(request, 'telephony/index.html')

# def locations(request):
#     form = LocationForm(request.POST or None)
#     if form.is_valid():
#         form.save()
#         # Handle form processing
    
#     locations = Location.objects.all()
#     context = {
#         'form': form,
#         'locations': locations,
#         'google_api_key': settings.GOOGLE_API_KEY,
#     }
#     return render(request, 'telephony/locations.html', context)

# views.py

# views.py

def locations(request):
    locations = Location.objects.all()
    if request.method == 'POST':
        location_id = request.POST.get('location_id')
        if location_id:
            location = get_object_or_404(Location, pk=location_id)
            form = LocationForm(request.POST, instance=location)
        else:
            form = LocationForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('locations')
    else:
        form = LocationForm()

    return render(request, 'telephony/locations.html', {'form': form, 'locations': locations})

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

def verify_location(location):
    # Logic to verify the location using an API (e.g., Google Maps API)
    # For simplicity, let's assume the location is verified successfully
    location.verified_location = True
    location.save()

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
            api_key = 'GOOGLE_API_KEY'
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