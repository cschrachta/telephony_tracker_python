import googlemaps
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView, View
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Location, ServiceProvider, CircuitDetail, PhoneNumber, Country, LocationFunction, ServiceProviderRep
from .templatetags import custom_filters
from .forms import CircuitDetailForm, LocationForm, SearchForm, PhoneNumberForm, CountryForm, ServiceProviderForm, LocationFunctionForm, ServiceProviderRepForm
from .utils import validate_address

logger = logging.getLogger(__name__)

# Home View
def index(request):
    context = {
        'view_name': 'index',
        'show_form': False,
        'show_table': False,
        'table_class': None,  # Add this to prevent template errors
        'clear_view_url': None,  # Add this to prevent template errors
        'form_fields': None,  # Add this to prevent template errors
    }
    print(context)
    return render(request, 'telephony/index.html', context)


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


#Country Views
def country_list(request):
    countries = Country.objects.all()
    context = {
        'view_name': 'country_list',
        'show_form': False,
        'show_table': True,
        'clear_view_url': 'countries',  # Add this
        'form_fields': None,
        'countries': countries,
    }
    return render(request, 'telephony/country_list.html', context)



class ServiceProviderListView(ListView):
    model = ServiceProvider
    form_class = ServiceProviderForm
    template_name = 'telephony/service_provider.html'
    context_object_name = 'items'
    success_url = reverse_lazy('telephony:service_provider')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ServiceProviderForm()
        context['items'] = ServiceProvider.objects.all() 
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:service_provider',
            'new_url': 'telephony:service_provider_new',
            'edit_url': 'telephony:service_provider_edit',
            'delete_url': 'telephony:delete_service_provider',
            'clear_view_url': 'service_provider',
            'table_class': 'service_providers-table',
            'table_headers': ['Provider', 'Support Number', 'Contract Number', 'Contract Details', 'Website', 'Notes'],
            'table_fields': ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes'],
            'form_class': 'service_provider-form',
            'form_fields': ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes'],
        })
        return context
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class ServiceProviderCreateView(CreateView):
    model = ServiceProvider
    form_class = ServiceProviderForm
    template_name = 'telephony/service_provider.html'
    context_object_name = 'items'
    success_url = reverse_lazy('telephony:service_provider')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ServiceProviderForm()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:service_provider',
            'new_url': 'telephony:service_provider_new',
            'edit_url': 'telephony:service_provider_edit',
            'delete_url': 'telephony:delete_service_provider',
            'clear_view_url': 'service_provider',
            'table_class': 'service_providers-table',
            'table_headers': ['Provider', 'Support Number', 'Contract Number', 'Contract Details', 'Website', 'Notes'],
            'table_fields': ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes'],
            'form_class': 'service_provider-form',
            'form_fields': ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes'],
        })
        return context
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class ServiceProviderUpdateView(UpdateView):
    model = ServiceProvider
    form_class = ServiceProviderForm
    template_name = 'telephony/service_provider.html'
    success_url = reverse_lazy('telephony:service_provider')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['items'] = ServiceProvider.objects.all() 
        context['object'] = self.get_object()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:service_provider',
            'new_url': 'telephony:service_provider_new',
            'edit_url': 'telephony:service_provider_edit',
            'delete_url': 'telephony:delete_service_provider',
            'clear_view_url': 'service_provider',
            'table_class': 'service_providers-table',
            'table_headers': ['Provider', 'Support Number', 'Contract Number', 'Contract Details', 'Website', 'Notes'],
            'table_fields': ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes'],
            'form_class': 'service_provider-form',
            'form_fields': ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes'],
        })
        return context
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ServiceProviderDetailView(DetailView):
    model = ServiceProvider

    def get(self, request, *args, **kwargs):
        service_provider = self.get_object()
        data = {
            'provider_name': service_provider.provider_name,
            'support_number': service_provider.support_number,
            'contract_number': service_provider.contract_number,
            'contract_details': service_provider.contract_details,
            'website_url': service_provider.website_url,
            'notes': service_provider.notes,
        }
        return JsonResponse(data)

class ServiceProviderDeleteView(DeleteView):
    model = ServiceProvider
    success_url = reverse_lazy('telephony:service_provider')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return JsonResponse({'result': 'success'})
    


class ServiceProviderRepListView(ListView):
    model = ServiceProviderRep
    form_class = ServiceProviderRepForm
    template_name = 'telephony/service_provider_rep.html'
    context_object_name = 'items'
    success_url = reverse_lazy('telephony:service_provider_rep')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ServiceProviderRepForm()
        context['items'] = ServiceProviderRep.objects.all() 
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:service_provider_rep',
            'new_url': 'telephony:service_provider_rep_new',
            'edit_url': 'telephony:service_provider_rep_edit',
            'delete_url': 'telephony:service_provider_rep_delete',
            'clear_view_url': 'service_provider_rep',
            'table_class': 'service_provider_rep-table',
            'table_headers': ['Provider', 'Representative Name', 'Contact Number', 'Contract Email', 'Notes'],
            'table_fields': ['provider', 'account_rep_name', 'account_rep_phone', 'account_rep_email', 'notes'],
            'form_class': 'service_provider_rep-form',
            'form_fields': ['provider', 'account_rep_name', 'account_rep_phone', 'account_rep_email', 'notes'],
        })
        return context
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class ServiceProviderRepCreateView(CreateView):
    model = ServiceProviderRep
    form_class = ServiceProviderRepForm
    template_name = 'telephony/service_provider_rep.html'
    context_object_name = 'items'
    success_url = reverse_lazy('telephony:service_provider_rep')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ServiceProviderRepForm()
        context['items'] = ServiceProviderRep.objects.all() 
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:service_provider_rep',
            'new_url': 'telephony:service_provider_rep_new',
            'edit_url': 'telephony:service_provider_rep_edit',
            'delete_url': 'telephony:service_provider_rep_delete',
            'clear_view_url': 'service_provider_rep',
            'table_class': 'service_provider_rep-table',
            'table_headers': ['Provider', 'Representative Name', 'Contact Number', 'Contract Email', 'Notes'],
            'table_fields': ['provider', 'account_rep_name', 'account_rep_phone', 'account_rep_email', 'notes'],
            'form_class': 'service_provider_rep-form',
            'form_fields': ['provider', 'account_rep_name', 'account_rep_phone', 'account_rep_email', 'notes'],
        })
        return context
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class ServiceProviderRepUpdateView(UpdateView):
    model = ServiceProviderRep
    form_class = ServiceProviderRepForm
    template_name = 'telephony/service_provider_rep.html'
    context_object_name = 'items'
    success_url = reverse_lazy('telephony:service_provider_rep')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ServiceProviderRepForm()
        context['items'] = ServiceProviderRep.objects.all() 
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:service_provider_rep',
            'new_url': 'telephony:service_provider_rep_new',
            'edit_url': 'telephony:service_provider_rep_edit',
            'delete_url': 'telephony:service_provider_rep_delete',
            'clear_view_url': 'service_provider_rep',
            'table_class': 'service_provider_rep-table',
            'table_headers': ['Provider', 'Representative Name', 'Contact Number', 'Contract Email', 'Notes'],
            'table_fields': ['provider', 'account_rep_name', 'account_rep_phone', 'account_rep_email', 'notes'],
            'form_class': 'service_provider_rep-form',
            'form_fields': ['provider', 'account_rep_name', 'account_rep_phone', 'account_rep_email', 'notes'],
        })
        return context
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ServiceProviderRepDetailView(DetailView):
    model = ServiceProviderRep

    def get(self, request, *args, **kwargs):
        service_provider_rep = self.get_object()
        data = {
            'provider': service_provider_rep.provider,
            'account_rep_name': service_provider_rep.support_number,
            'account_rep_phone': service_provider_rep.contract_number,
            'accouht_rep_email': service_provider_rep.contract_details,
            'notes': service_provider_rep.notes,
        }
        return JsonResponse(data)

class ServiceProviderRepDeleteView(DeleteView):
    model = ServiceProviderRep
    success_url = reverse_lazy('telephony:service_provider_rep')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return JsonResponse({'result': 'success'})
    


class LocationListView(ListView):
    model = Location
    form_class = LocationForm
    template_name = 'telephony/locations.html'
    context_object_name = 'items'
    success_url = reverse_lazy('telephony:locations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LocationForm()
        context['items'] = Location.objects.all() 
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:locations',
            'new_url': 'telephony:location_new',
            'edit_url': 'telephony:location_edit',
            'delete_url': 'telephony:delete_location',
            'clear_view_url': 'locations',
            'table_class': 'locations-table',
            'table_headers': ['Name', 'Display Name', 'Address', 'Street/Road', 'City', 'State', 'Country', 'Postcode', 'Verified'],
            'table_fields': ['name', 'display_name', 'house_number', 'road', 'city', 'state', 'country', 'postcode', 'verified_location'],
            'form_class': 'location-form',
            'form_fields': ['name', 'display_name', 'house_number', 'road', 'city', 'state', 'postcode', 'country', 'notes'],
        })
        return context

class LocationCreateView(CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'telephony/locations.html'
    success_url = reverse_lazy('telephony:locations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['items'] = Location.objects.all()
        context['object'] = self.get_object()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:locations',
            'new_url': 'telephony:location_new',
            'edit_url': 'telephony:location_edit',
            'delete_url': 'telephony:delete_location',
            'clear_view_url': 'locations',
            'table_class': 'locations-table',
            'table_headers': ['Name', 'Display Name', 'Address', 'Street/Road', 'City', 'State', 'Country', 'Postcode', 'Verified'],
            'table_fields': ['name', 'display_name', 'house_number', 'road', 'city', 'state', 'country', 'postcode', 'verified_location'],
            'form_class': 'location-form',
            'form_fields': ['name', 'display_name', 'house_number', 'road', 'road_suffix', 'city', 'county', 'state', 'state_abbreviation', 'postcode', 'country', 'latitude', 'longitude', 'timezone', 'contact_person', 'contact_email', 'contact_phone', 'location_function', 'verified_location', 'notes'],
        })
        return context

class LocationUpdateView(UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'telephony/locations.html'
    success_url = reverse_lazy('telephony:locations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['items'] = Location.objects.all() 
        context['object'] = self.get_object()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:locations',
            'new_url': 'telephony:location_new',
            'edit_url': 'telephony:location_edit',
            'delete_url': 'telephony:delete_location',
            'clear_view_url': 'locations',
            'table_class': 'locations-table',
            'table_headers': ['Name', 'Display Name', 'Address', 'Street/Road', 'City', 'State', 'Country', 'Postcode', 'Verified'],
            'table_fields': ['name', 'display_name', 'house_number', 'road', 'city', 'state', 'country', 'postcode', 'verified_location'],
            'form_class': 'location-form',
            'form_fields': ['name', 'display_name', 'house_number', 'road', 'city', 'state', 'postcode', 'country', 'verified_location'],
        })
        return context

class LocationDetailView(DetailView):
    model = Location

    def get(self, request, *args, **kwargs):
        location = self.get_object()
        data = {
            'name': location.name,
            'display_name': location.display_name,
            'house_number': location.house_number,
            'road': location.road,
            'city': location.city,
            'state': location.state,
            'country': location.country.name,
            'postcode': location.postcode,
            'verified_location': location.verified_location,
        }
        return JsonResponse(data)

class LocationDeleteView(DeleteView):
    model = Location
    success_url = reverse_lazy('telephony:locations')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return JsonResponse({'result': 'success'})

class ValidateLocationView(View):
    def post(self, request, pk, *args, **kwargs):
        location = get_object_or_404(Location, pk=pk)
        address = f"{location.house_number} {location.road}, {location.city}, {location.state}, {location.country.name} {location.postcode}"
        formatted_address, is_valid = validate_address(address)
        if is_valid:
            location.verified_location = True
            location.save()
            messages.success(request, "Address has been validated.")
        else:
            messages.error(request, "Address could not be validated.")
        return HttpResponseRedirect(reverse_lazy('telephony:locations'))


class LocationFunctionListView(ListView):
    model = LocationFunction
    template_name = 'telephony/location_function.html'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LocationFunctionForm()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:location_function',
            'new_url': 'telephony:location_function_new',
            'edit_url': 'telephony:location_function_edit',
            'delete_url': 'telephony:location_function_delete',
            'clear_view_url': 'location_functions',
            'table_class': 'location-function-table',
            'table_headers': ['Name', 'Function Code', 'Description'],
            'table_fields': ['function_name', 'function_code', 'description'],
            'form_class': 'location-function-form',
            'form_fields': ['function_name', 'description'],
        })
        return context

class LocationFunctionCreateView(CreateView):
    model = LocationFunction
    form_class = LocationFunctionForm
    template_name = 'telephony/location_function.html'
    success_url = reverse_lazy('telephony:location_function_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LocationFunctionForm()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:location_function_list',
            'new_url': 'telephony:location_function_new',
            'edit_url': 'telephony:location_function_edit',
            'delete_url': 'telephony:location_function_delete',
            'clear_view_url': 'location_functions',
            'table_class': 'location-functions-table',
            'table_headers': ['Function Name', 'Description'],
            'table_fields': ['function_name', 'description'],
            'form_class': 'location-function-form',
            'form_fields': ['function_name', 'description'],
        })
        return context

class LocationFunctionUpdateView(UpdateView):
    model = LocationFunction
    form_class = LocationFunctionForm
    template_name = 'telephony/location_function.html'
    success_url = reverse_lazy('telephony:location_function_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['items'] = LocationFunction.objects.all()
        context['object'] = self.get_object()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:location_function_list',
            'new_url': 'telephony:location_function_new',
            'edit_url': 'telephony:location_function_edit',
            'delete_url': 'telephony:location_function_delete',
            'clear_view_url': 'location_functions',
            'table_class': 'location-functions-table',
            'table_headers': ['Function Name', 'Description'],
            'table_fields': ['function_name', 'description'],
            'form_class': 'location-function-form',
            'form_fields': ['function_name', 'description'],
        })
        return context

class LocationFunctionDeleteView(DeleteView):
    model = LocationFunction
    success_url = reverse_lazy('telephony:location_function')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return JsonResponse({'result': 'success'})






class PhoneNumberListView(ListView):
    model = PhoneNumber
    form_class = PhoneNumberForm
    template_name = 'telephony/phone_numbers.html'
    context_object_name = 'items'
    success_url = reverse_lazy('telephony:phone_numbers')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PhoneNumberForm()
        context['items'] = PhoneNumber.objects.exclude(pk=None)
        print(context['items'])
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:phone_numbers',
            'new_url': 'telephony:phone_number_new',
            'edit_url': 'telephony:phone_number_edit',
            'delete_url': 'telephony:delete_phone_number',
            'clear_view_url': 'phone_numbers',
            'table_class': 'phone-numbers-table',
            'table_headers': ['Directory Number', 'Country', 'Subscriber Number', 'Location', 'Usage Type', 'Status'],
            'table_fields': ['directory_number', 'country', 'subscriber_number', 'service_location', 'usage_type', 'status'],
            'form_class': 'phone-number-form',
            'form_fields': ['directory_number', 'country', 'subscriber_number', 'service_location', 'usage_type', 'status'],
        })
        return context

class PhoneNumberCreateView(CreateView):
    model = PhoneNumber
    form_class = PhoneNumberForm
    template_name = 'telephony/phone_numbers.html'
    success_url = reverse_lazy('telephony:phone_numbers')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PhoneNumberForm()
        context['items'] = PhoneNumber.objects.all()
        context['object'] = self.get_object()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:phone_numbers',
            'new_url': 'telephony:phone_number_new',
            'edit_url': 'telephony:phone_number_edit',
            'delete_url': 'telephony:delete_phone_number',
            'clear_view_url': 'phone_numbers',
            'table_class': 'phone-numbers-table',
            'table_headers': ['Directory Number', 'Country', 'Subscriber Number', 'Location', 'Usage Type', 'Status'],
            'table_fields': ['directory_number', 'country', 'subscriber_number', 'service_location', 'usage_type', 'status'],
            'form_class': 'phone-number-form',
            'form_fields': ['directory_number', 'country', 'subscriber_number', 'service_location', 'usage_type', 'status'],
        })
        return context

class PhoneNumberUpdateView(UpdateView):
    model = PhoneNumber
    form_class = PhoneNumberForm
    template_name = 'telephony/phone_numbers.html'
    success_url = reverse_lazy('telephony:phone_numbers')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['items'] = PhoneNumber.objects.all() 
        context['object'] = self.get_object()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': 'telephony:phone_numbers',
            'new_url': 'telephony:phone_number_new',
            'edit_url': 'telephony:phone_number_edit',
            'delete_url': 'telephony:delete_phone_number',
            'clear_view_url': 'phone_numbers',
            'table_class': 'phone-numbers-table',
            'table_headers': ['Directory Number', 'Country', 'Subscriber Number', 'Location', 'Usage Type', 'Status'],
            'table_fields': ['directory_number', 'country', 'subscriber_number', 'service_location', 'usage_type', 'status'],
            'form_class': 'phone-number-form',
            'form_fields': ['directory_number', 'country', 'subscriber_number', 'service_location', 'usage_type', 'status'],
        })
        return context

class PhoneNumberDetailView(DetailView):
    model = PhoneNumber

    def get(self, request, *args, **kwargs):
        phone_number = self.get_object()
        data = {
            'directory_number': phone_number.directory_number,
            'country': phone_number.country.name,
            'subscriber_number': phone_number.subscriber_number,
            'service_location': phone_number.service_location.name,
            'usage_type': phone_number.usage_type.usage_type,
            'status': phone_number.status,
        }
        return JsonResponse(data)

class PhoneNumberDeleteView(DeleteView):
    model = PhoneNumber
    success_url = reverse_lazy('telephony:phone_numbers')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return JsonResponse({'result': 'success'})
    

