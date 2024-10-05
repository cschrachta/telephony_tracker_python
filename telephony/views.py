import googlemaps
import logging
import inflection
import json
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView, View
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Location, ServiceProvider, CircuitDetail, PhoneNumber, PhoneNumberRange, Country, LocationFunction, ServiceProviderRep, UsageType, SwitchType, ConnectionType
from telephony.templatetags import custom_filters
from .forms import CircuitDetailForm, LocationForm, SearchForm, PhoneNumberForm, PhoneNumberRangeForm, CountryForm, ServiceProviderForm, LocationFunctionForm, ServiceProviderRepForm, UsageTypeForm, SwitchTypeForm, ConnectionTypeForm
from .utils import validate_address

logger = logging.getLogger(__name__)

# Home View
def index(request):
    context = {
        'view_name': 'index',
        'show_form': False,
        'show_table': False,
        'table_class': None,
        'clear_view_url': None,
        'form_fields': None,
    }
    return render(request, 'telephony/index.html', context)


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



@require_POST
def generic_bulk_update(request, model_class):
    data = json.loads(request.body)
    ids = data.get('ids', [])
    update_data = data.get('data', {})

    # Remove any fields you don't want to update
    update_data.pop('directory_number', None)

    model_class.objects.filter(id__in=ids).update(**update_data)
    return JsonResponse({'success': True})

@require_POST
def generic_bulk_delete(request, model_class):
    data = json.loads(request.body)
    ids = data.get('ids', [])

    model_class.objects.filter(id__in=ids).delete()
    return JsonResponse({'success': True})




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
            'bulk_edit_url': f'telephony:{model_name_snake_case}_batch_edit',
            'bulk_delete_url': f'telephony:{model_name_snake_case}_batch_delete',
            'clear_view_url': reverse_lazy(f'telephony:{model_name_snake_case}'),
            'table_class': f'{model_name_snake_case}-table',
            'table_headers': self.table_headers,
            'table_fields': self.table_fields,
            'form_class': f'{model_name_snake_case}-form',
            'form_fields': [field.name for field in self.model._meta.fields],
            'linkable_fields': [
                ('directory_number', 'telephony:phone_number_edit'),
                ('service_provider', 'telephony:service_provider_edit'),
                ('provider_name', 'telephony:service_provider_edit'),
                ('location', 'telephony:location_edit'),
                ('location', 'telephony:location_edit'),
            ],
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
            'bulk_edit_url': f'telephony:{model_name_snake_case}_batch_edit',
            'bulk_delete_url': f'telephony:{model_name_snake_case}_batch_delete',
            'clear_view_url': reverse_lazy(f'telephony:{model_name_snake_case}'),
            'table_class': f'{model_name_snake_case}-table',
            'table_headers': self.table_headers,
            'table_fields': self.table_fields,
            'form_class': f'{model_name_snake_case}-form',
            'form_fields': [field.name for field in self.model._meta.fields],
            'linkable_fields': [
                ('directory_number', 'telephony:phone_number_edit'),
                ('service_provider', 'telephony:service_provider_edit'),
                ('provider_name', 'telephony:service_provider_edit'),
                ('location', 'telephony:location_edit'),
                ('location', 'telephony:location_edit'),
            ],
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
            'bulk_edit_url': f'telephony:{model_name_snake_case}_batch_edit',
            'bulk_delete_url': f'telephony:{model_name_snake_case}_batch_delete',
            'clear_view_url': reverse_lazy(f'telephony:{model_name_snake_case}'),
            'table_class': f'{model_name_snake_case}-table',
            'table_headers': self.table_headers,
            'table_fields': self.table_fields,
            'form_class': f'{model_name_snake_case}-form',
            'form_fields': [field.name for field in self.model._meta.fields],
            'linkable_fields': [
                ('directory_number', 'telephony:phone_number_edit'),
                ('service_provider', 'telephony:service_provider_edit'),
                ('provider_name', 'telephony:service_provider_edit'),
                ('location', 'telephony:location_edit'),
                ('location', 'telephony:location_edit'),
            ],
            
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
    Base class for DeleteView that handles common context data setup and redirection.
    """
    model = None
    success_url = None

    def post(self, request, *args, **kwargs):
        self.success_url = self.get_success_url()
        return super().post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Perform the delete operation
        response = super().delete(request, *args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        model_name_snake_case = inflection.underscore(self.model._meta.object_name)
        return reverse_lazy(f'telephony:{model_name_snake_case}')


class BulkDeleteView(View):
    model = None

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('ids[]')
        if ids:
            self.model.objects.filter(id__in=ids).delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'No IDs provided for deletion.'})
        

class BulkUpdateView(View):
    model = None
    fields_to_update = []

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('ids[]')
        update_data = request.POST.dict()

        # Remove non-update data (like csrfmiddlewaretoken, ids)
        for key in ['csrfmiddlewaretoken', 'ids']:
            update_data.pop(key, None)

        if ids and update_data:
            # Ensure only allowed fields are updated
            update_data = {key: value for key, value in update_data.items() if key in self.fields_to_update}

            # Update the records
            self.model.objects.filter(id__in=ids).update(**update_data)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'No IDs provided or no valid fields to update.'})


class ServiceProviderListView(BaseListView):
    model = ServiceProvider
    form_class = ServiceProviderForm
    table_headers = ['Provider', 'Support Number', 'Contract Number', 'Contract Details', 'Website', 'Notes']
    table_fields = ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes']
    form_fields = ['provider_name', 'support_number', 'contract_number', 'contract_details', 'website_url', 'notes']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'display_edit_links': True,
            'service_provider_edit_link': True,
            'phone_number_edit_link': True,
            'phone_number_range_edit_link': True,
            'location_edit_link': True,
            'location_function_edit_link': True,
            'usage_type_edit_link': True,
        })
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'display_edit_links': True,
            'service_provider_edit_link': True,
            'phone_number_edit_link': True,
            'phone_number_range_edit_link': True,
            'location_edit_link': True,
            'location_function_edit_link': True,
            'usage_type_edit_link': True,
        })
        return context

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
    table_headers = ['Site ID', 'House Number', 'Street/Road', 'City', 'State', 'Country', 'Postcode', 'Site ID', 'Trunk Access Code', 'Verified']
    table_fields = ['site_id', 'house_number', 'road', 'city', 'state', 'country', 'postcode', 'site_id', 'trunk_access_code', 'verified_location']
    form_fields = ['site_id', 'display_name', 'house_number', 'road', 'city', 'state', 'postcode', 'country', 'site_id', 'trunk_access_code', 'notes']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'display_edit_links': True,
            'service_provider_edit_link': True,
            'phone_number_edit_link': True,
            'phone_number_range_edit_link': True,
            'location_edit_link': True,
            'location_function_edit_link': True,
            'usage_type_edit_link': True,
        })
        return context
    
    def get_queryset(self):
        return Location.objects.all().order_by('site_id')

class LocationCreateView(BaseCreateView):
    model = Location
    form_class = LocationForm
    success_url = reverse_lazy('telephony:location')

class LocationUpdateView(BaseUpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'telephony/location.html'
    table_headers = ['Name', 'House Number', 'Street/Road', 'City', 'State', 'Country', 'Postcode', 'Site ID', 'Trunk Access Code', 'Verified']
    table_fields = ['name', 'house_number', 'road', 'city', 'state', 'country', 'postcode', 'site_id', 'trunk_access_code', 'verified_location']
    form_fields = ['name', 'house_number', 'road', 'city', 'state', 'postcode', 'country', 'site_id', 'trunk_access_code', 'notes']
    success_url = reverse_lazy('telephony:location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'display_edit_links': True,
            'service_provider_edit_link': True,
            'phone_number_edit_link': True,
            'phone_number_range_edit_link': True,
            'location_edit_link': True,
            'location_function_edit_link': True,
            'usage_type_edit_link': True,
        })
        return context
    
    def get_queryset(self):
        return Location.objects.all().order_by('site_id')

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
    form_fields = ['function_name', 'description']

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
        # 'Usage Type', 
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
        'location', 
        # 'usage_type', 
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
        'location',
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'display_edit_links': True,
            'service_provider_edit_link': True,
            'phone_number_edit_link': True,
            'phone_number_range_edit_link': True,
            'location_edit_link': True,
            'location_function_edit_link': True,
            'usage_type_edit_link': True,
        })
        return context


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
        # 'Usage Type', 
        # 'Status',
        'Assigned To',
        'service_provider',
        # 'Activation Date',
        # 'Deactivation Date',
        'Notes'
    ]
    table_fields = [
        'directory_number', 
        'country', 
        'subscriber_number', 
        'location', 
        # 'usage_type', 
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
        'location',
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
    
    def phone_number_edit(request, pk):
        phone_number = get_object_or_404(PhoneNumber, pk=pk)
        data = {field.name: getattr(phone_number, field.name) for field in PhoneNumber._meta.fields}
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'display_edit_links': True,
            'service_provider_edit_link': True,
            'phone_number_edit_link': True,
            'phone_number_range_edit_link': True,
            'location_edit_link': True,
            'location_function_edit_link': True,
            'usage_type_edit_link': True,
        })
        return context

class PhoneNumberDetailView(BaseDetailView):
    model = PhoneNumber

class PhoneNumberDeleteView(BaseDeleteView):
    model = PhoneNumber

class PhoneNumberBulkUpdateView(BulkUpdateView):
    model = PhoneNumber
    fields_to_update = ['usage_type', 'location', 'status', 'assigned_to']


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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'display_edit_links': True,
            'service_provider_edit_link': True,
            'phone_number_edit_link': True,
            'phone_number_range_edit_link': True,
            'location_edit_link': True,
            'location_function_edit_link': True,
            'usage_type_edit_link': True,
        })
        return context

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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'display_edit_links': True,
            'service_provider_edit_link': True,
            'phone_number_edit_link': True,
            'phone_number_range_edit_link': True,
            'location_edit_link': True,
            'location_function_edit_link': True,
            'usage_type_edit_link': True,
        })
        return context

class PhoneNumberRangeDetailView(BaseDetailView):
    model = PhoneNumberRange

class PhoneNumberRangeDeleteView(BaseDeleteView):
    model = PhoneNumberRange


class UsageTypeListView(BaseListView):
    model = UsageType
    form_class = UsageTypeForm
    template_name = 'telephony/usage_type.html'
    table_headers = ['usage_type', 'usage_for']
    table_fields = ['usage_type', 'usage_for']
    form_fields = ['usage_type', 'usage_for']

class UsageTypeCreateView(BaseCreateView):
    model = UsageType
    form_class = UsageTypeForm
    template_name = 'telephony/usage_type.html'
    success_url = reverse_lazy('telephony:usage_type')

class UsageTypeUpdateView(BaseUpdateView):
    model = UsageType
    form_class = UsageTypeForm
    template_name = 'telephony/usage_type.html'
    table_headers = ['usage_type', 'usage_for']
    table_fields = ['usage_type', 'usage_for']
    form_fields = ['usage_type', 'usage_for']
    success_url = reverse_lazy('telephony:usage_type')

class UsageTypeDetailView(BaseDetailView):
    model = UsageType

class UsageTypeDeleteView(BaseDeleteView):
    model = UsageType
    success_url = reverse_lazy('telephony:usage_type')


class CircuitListView(BaseListView):
    model = CircuitDetail
    form_class = CircuitDetailForm
    template_name = 'telephony/usage_type.html'
    table_headers = ['usage_type', 'usage_for']
    table_fields = ['usage_type', 'usage_for']
    form_fields = ['usage_type', 'usage_for']

class CircuitCreateView(BaseCreateView):
    model = CircuitDetail
    form_class = CircuitDetailForm
    template_name = 'telephony/usage_type.html'
    success_url = reverse_lazy('telephony:circuits')

class CircuitUpdateView(BaseUpdateView):
    model = CircuitDetail
    form_class = CircuitDetailForm
    template_name = 'telephony/usage_type.html'
    table_headers = ['usage_type', 'usage_for']
    table_fields = ['usage_type', 'usage_for']
    form_fields = ['usage_type', 'usage_for']
    success_url = reverse_lazy('telephony:circuits')

class CircuitDetailView(BaseDetailView):
    model = CircuitDetail

class CircuitDeleteView(BaseDeleteView):
    model = CircuitDetail
    success_url = reverse_lazy('telephony:circuits')

class SwitchTypeListView(BaseListView):
    model = SwitchType
    form_class = SwitchTypeForm
    template_name = 'telephony/switch_type.html'
    table_headers = ['switch_type_name', 'description']
    table_fields = ['switch_type_name', 'description']
    form_fields = ['switch_type_name', 'description']

class SwitchTypeCreateView(BaseCreateView):
    model = SwitchType
    form_class = SwitchTypeForm
    template_name = 'telephony/switch_type.html'
    success_url = reverse_lazy('telephony:switch_type')

class SwitchTypeUpdateView(BaseUpdateView):
    model = SwitchType
    form_class = SwitchTypeForm
    template_name = 'telephony/switch_type.html'
    table_headers = ['switch_type_name', 'description']
    table_fields = ['switch_type_name', 'description']
    form_fields = ['switch_type_name', 'description']
    success_url = reverse_lazy('telephony:switch_type')

class SwitchTypeDetailView(BaseDetailView):
    model = SwitchType

class SwitchTypeDeleteView(BaseDeleteView):
    model = SwitchType
    success_url = reverse_lazy('telephony:switch_type')

class ConnectionTypeListView(BaseListView):
    model = ConnectionType
    form_class = ConnectionTypeForm
    template_name = 'telephony/connection_type.html'
    table_headers = ['connection_type_name', 'description']
    table_fields = ['connection_type_name', 'description']
    form_fields = ['connection_type_name', 'description']

class ConnectionTypeCreateView(BaseCreateView):
    model = ConnectionType
    form_class = ConnectionTypeForm
    template_name = 'telephony/connection_type.html'
    success_url = reverse_lazy('telephony:connection_type')

class ConnectionTypeUpdateView(BaseUpdateView):
    model = ConnectionType
    form_class = ConnectionTypeForm
    template_name = 'telephony/connection_type.html'
    table_headers = ['connection_type_name', 'description']
    table_fields = ['connection_type_name', 'description']
    form_fields = ['connection_type_name', 'description']
    success_url = reverse_lazy('telephony:connection_type')

class ConnectionTypeDetailView(BaseDetailView):
    model = ConnectionType

class ConnectionTypeDeleteView(BaseDeleteView):
    model = ConnectionType
    success_url = reverse_lazy('telephony:connection_type')
