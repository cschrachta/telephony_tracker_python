import googlemaps
import logging
import inflection
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView, View
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Location, ServiceProvider, CircuitDetail, PhoneNumber, PhoneNumberRange, Country, LocationFunction, ServiceProviderRep
from .templatetags import custom_filters
from .forms import CircuitDetailForm, LocationForm, SearchForm, PhoneNumberForm, PhoneNumberRangeForm, CountryForm, ServiceProviderForm, LocationFunctionForm, ServiceProviderRepForm
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
    

class BaseListView(ListView):
    """
    Base class for ListView that handles common context data setup.
    """
    model = None
    form_class = None
    template_name = None
    context_object_name = 'items'
    table_headers = []
    table_fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_snake_case = inflection.underscore(self.model._meta.object_name)
        context['form'] = self.form_class()
        context['items'] = self.model.objects.all()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': self.request.resolver_match.view_name,
            'new_url': f'telephony:{model_name_snake_case}_new',
            'edit_url': f'telephony:{model_name_snake_case}_edit',
            'delete_url': f'telephony:{model_name_snake_case}_delete',
            'clear_view_url': reverse_lazy(f'telephony:{model_name_snake_case}'),
            'table_class': f'{model_name_snake_case}-table',
            'table_headers': self.table_headers,
            'table_fields': self.table_fields,
            'form_class': f'{model_name_snake_case}-form',
            'form_fields': [field.name for field in self.model._meta.fields],
        })
        return context
    
    def get_template_names(self):
        model_name_str = str(self.model._meta.object_name)  # Ensure it's a string
        model_name_snake_case = inflection.underscore(model_name_str)
        return [f'telephony/{model_name_snake_case}.html']
    
    def get_success_url(self):
        model_name_snake_case = inflection.underscore(self.model._meta.object_name)
        return reverse_lazy(f'telephony:{model_name_snake_case}')

class BaseCreateView(CreateView):
    """
    Base class for CreateView that handles common context data setup.
    """
    model = None
    form_class = None
    template_name = None
    success_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_snake_case = inflection.underscore(self.model._meta.object_name)
        context['form'] = self.form_class()
        context['items'] = self.model.objects.all()
        context['object'] = self.get_object()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': self.request.resolver_match.view_name,
            'new_url': f'telephony:{model_name_snake_case}_new',
            'edit_url': f'telephony:{model_name_snake_case}_edit',
            'delete_url': f'telephony:{model_name_snake_case}_delete',
            'clear_view_url': reverse_lazy(f'telephony:{model_name_snake_case}'),
            'table_class': f'{model_name_snake_case}-table',
            'table_headers': self.table_headers,
            'table_fields': self.table_fields,
            'form_class': f'{model_name_snake_case}-form',
            'form_fields': [field.name for field in self.model._meta.fields],
        })
        return context
    
    def get_template_names(self):
        model_name_str = str(self.model._meta.object_name)  # Ensure it's a string
        model_name_snake_case = inflection.underscore(model_name_str)
        return [f'telephony/{model_name_snake_case}.html']
    
    def get_success_url(self):
        model_name_snake_case = inflection.underscore(self.model._meta.object_name)
        return reverse_lazy(f'telephony:{model_name_snake_case}')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class BaseUpdateView(UpdateView):
    """
    Base class for UpdateView that handles common context data setup.
    """
    model = None
    form_class = None
    template_name = None
    success_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name_snake_case = inflection.underscore(self.model._meta.object_name)
        context['form'] = self.get_form()
        context['items'] = self.model.objects.all()
        context['object'] = self.get_object()
        context.update({
            'show_form': True,
            'show_table': True,
            'view_name': self.request.resolver_match.view_name,
            'new_url': f'telephony:{model_name_snake_case}_new',
            'edit_url': f'telephony:{model_name_snake_case}_edit',
            'delete_url': f'telephony:{model_name_snake_case}_delete',
            'clear_view_url': reverse_lazy(f'telephony:{model_name_snake_case}'),
            'table_class': f'{model_name_snake_case}-table',
            'table_headers': self.table_headers,
            'table_fields': self.table_fields,
            'form_class': f'{model_name_snake_case}-form',
            'form_fields': [field.name for field in self.model._meta.fields],
        })
        return context
    
    def get_template_names(self):
        model_name_str = str(self.model._meta.object_name)  # Ensure it's a string
        model_name_snake_case = inflection.underscore(model_name_str)
        return [f'telephony/{model_name_snake_case}.html']
    
    def get_success_url(self):
        model_name_snake_case = inflection.underscore(self.model._meta.object_name)
        return reverse_lazy(f'telephony:{model_name_snake_case}')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    

class BaseDetailView(DetailView):
    """
    Base class for DetailView that returns JSON data.
    """
    model = None

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        data = {field.name: getattr(obj, field.name) for field in self.model._meta.fields}
        return JsonResponse(data)

class BaseDeleteView(DeleteView):
    """
    Base class for DeleteView that returns a JSON response.
    """
    model = None
    success_url = None

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return JsonResponse({'result': 'success'})




class ServiceProviderListView(BaseListView):
    model = ServiceProvider
    form_class = ServiceProviderForm
    table_headers = ['Provider', 'Support Number', 'Contract Number', 'Contract Details', 'Website', 'Notes']
    table_fields = ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes']
    form_fields = ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes']

class ServiceProviderCreateView(BaseCreateView):
    model = ServiceProvider
    form_class = ServiceProviderForm
    success_url = reverse_lazy('telephony:service_provider')

class ServiceProviderUpdateView(BaseUpdateView):
    model = ServiceProvider
    form_class = ServiceProviderForm
    table_headers = ['Provider', 'Support Number', 'Contract Number', 'Contract Details', 'Website', 'Notes']
    table_fields = ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes']
    success_url = reverse_lazy('telephony:service_provider')

class ServiceProviderDetailView(BaseDetailView):
    model = ServiceProvider

class ServiceProviderDeleteView(BaseDeleteView):
    model = ServiceProvider
    success_url = reverse_lazy('telephony:service_provider')


class ServiceProviderRepListView(BaseListView):
    model = ServiceProviderRep
    form_class = ServiceProviderRepForm
    table_headers = ['Representative', 'Contact Number', 'Contact Email', 'Provider', 'Notes']
    table_fields = ['account_rep_name', 'account_rep_phone', 'account_rep_email', 'provider', 'notes']

class ServiceProviderRepCreateView(BaseCreateView):
    model = ServiceProviderRep
    form_class = ServiceProviderRepForm
    success_url = reverse_lazy('telephony:service_provider_rep')

class ServiceProviderRepUpdateView(BaseUpdateView):
    model = ServiceProviderRep
    form_class = ServiceProviderRepForm
    table_headers = ['Representative', 'Contact Number', 'Contact Email', 'Provider', 'Notes']
    table_fields = ['account_rep_name', 'account_rep_phone', 'account_rep_email', 'provider', 'notes']
    success_url = reverse_lazy('telephony:service_provider_rep')

class ServiceProviderRepDetailView(BaseDetailView):
    model = ServiceProviderRep

class ServiceProviderRepDeleteView(BaseDeleteView):
    model = ServiceProviderRep
    form_class = ServiceProviderRepForm
    success_url = reverse_lazy('telephony:service_provider_rep')



class LocationListView(BaseListView):
    model = Location
    form_class = LocationForm
    table_headers = ['Name', 'Display Name', 'Address', 'Street/Road', 'City', 'State', 'Country', 'Postcode', 'Verified']
    table_fields = ['name', 'display_name', 'house_number', 'road', 'city', 'state', 'country', 'postcode', 'verified_location']
    form_fields = ['name', 'display_name', 'house_number', 'road', 'city', 'state', 'postcode', 'country', 'notes']

class LocationCreateView(BaseCreateView):
    model = Location
    form_class = LocationForm
    success_url = reverse_lazy('telephony:location')

class LocationUpdateView(BaseUpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'telephony/location.html'
    table_headers = ['Name', 'Address', 'Street/Road', 'City', 'State', 'Country', 'Postcode', 'Verified']
    table_fields = ['display_name', 'house_number', 'road', 'city', 'state', 'country', 'postcode', 'verified_location']
    form_fields = ['name', 'display_name', 'house_number', 'road', 'city', 'state', 'postcode', 'country', 'notes']
    success_url = reverse_lazy('telephony:location')

class LocationDetailView(BaseDetailView):
    model = Location

class LocationDeleteView(BaseDeleteView):
    model = Location
    success_url = reverse_lazy('telephony:location')


class LocationFunctionListView(BaseListView):
    model = LocationFunction
    form_class = LocationFunctionForm
    template_name = 'telephony/location_function.html'
    table_headers = ['Name', 'Function Code', 'Description']
    table_fields = ['function_name', 'function_code', 'description']
    form_fields = ['function_name', 'description'],

class LocationFunctionCreateView(BaseCreateView):
    model = LocationFunction
    form_class = LocationFunctionForm
    template_name = 'telephony/location_function.html'
    success_url = reverse_lazy('telephony:location_function')

class LocationFunctionUpdateView(BaseUpdateView):
    model = LocationFunction
    form_class = LocationFunctionForm
    template_name = 'telephony/location_function.html'
    table_headers = ['Name', 'Function Code', 'Description']
    table_fields = ['function_name', 'function_code', 'description']
    form_fields = ['function_name', 'description'],
    success_url = reverse_lazy('telephony:location_function')

class LocationFunctionDetailView(BaseDetailView):
    model = LocationFunction

class LocationFunctionDeleteView(BaseDeleteView):
    model = LocationFunction
    success_url = reverse_lazy('telephony:location_function')


class PhoneNumberListView(BaseListView):
    model = PhoneNumber
    form_class = PhoneNumberForm
    table_headers = [
        'Directory Number', 
        'Country', 
        'Subscriber Number', 
        'Service Location', 
        'Usage Type', 
        # 'Status',
        'Assigned To',
        'Provider',
        # 'Activation Date',
        # 'Deactivation Date',
        'Notes'
    ]
    table_fields = [
        'directory_number', 
        'country', 
        'subscriber_number', 
        'service_location', 
        'usage_type', 
        # 'status',
        'assigned_to',
        'service_provider',
        # 'activation_date',
        # 'deactivation_date',
        'notes'
    ]
    form_fields = [
        'directory_number',
        'country',
        'subscriber_number',
        'service_location',
        'usage_type',
        'status',
        'assigned_to',
        'activation_date',
        'deactivation_date',
        'notes',
        'service_provider',
        'phone_number_range',
        'circuit'
    ]

class PhoneNumberCreateView(BaseCreateView):
    model = PhoneNumber
    form_class = PhoneNumberForm

class PhoneNumberUpdateView(BaseUpdateView):
    model = PhoneNumber
    form_class = PhoneNumberForm
    table_headers = [
        'Directory Number', 
        'Country', 
        'Subscriber Number', 
        'Service Location', 
        'Usage Type', 
        'Status',
        'Assigned To',
        'Activation Date',
        'Deactivation Date',
        'Notes'
    ]
    table_fields = [
        'directory_number', 
        'country', 
        'subscriber_number', 
        'service_location', 
        'usage_type', 
        'status',
        'assigned_to',
        'activation_date',
        'deactivation_date',
        'notes'
    ]
    form_fields = [
        'directory_number',
        'country',
        'subscriber_number',
        'service_location',
        'usage_type',
        'status',
        'assigned_to',
        'activation_date',
        'deactivation_date',
        'notes',
        'service_provider',
        'phone_number_range',
        'circuit'
    ]

class PhoneNumberDetailView(BaseDetailView):
    model = PhoneNumber

class PhoneNumberDeleteView(BaseDeleteView):
    model = PhoneNumber



###############################################################################################################
class PhoneNumberRangeListView(BaseListView):
    model = PhoneNumberRange
    form_class = PhoneNumberRangeForm
    table_headers = [
        'Range Start Number',
        'Range End Number',
        'Country',
        'Provider',
        'Service Location', 
        'Usage Type', 
        'Notes'
    ]
    table_fields = [
        'start_number',
        'end_number',
        'country',
        'service_provider',
        'location',
        'usage_type', 
        'notes'
    ]
    form_fields = [
        'start_number',
        'end_number',
        'country',
        'service_provider',
        'location',
        'usage_type', 
        'notes'
    ]

class PhoneNumberRangeCreateView(BaseCreateView):
    model = PhoneNumberRange
    form_class = PhoneNumberRangeForm

class PhoneNumberRangeUpdateView(BaseUpdateView):
    model = PhoneNumberRange
    form_class = PhoneNumberRangeForm
    table_headers = [
        'Range Start Number',
        'Range End Number',
        'Country',
        'Provider',
        'Service Location', 
        'Usage Type', 
        'Notes'
    ]
    table_fields = [
        'start_number',
        'end_number',
        'country',
        'service_provider',
        'location',
        'usage_type', 
        'notes'
    ]
    form_fields = [
        'start_number',
        'end_number',
        'country',
        'service_provider',
        'location',
        'usage_type', 
        'notes'
    ]

class PhoneNumberRangeDetailView(BaseDetailView):
    model = PhoneNumberRange

class PhoneNumberRangeDeleteView(BaseDeleteView):
    model = PhoneNumberRange
