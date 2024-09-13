from django.urls import path
from .views import (
  ServiceProviderListView, ServiceProviderCreateView, ServiceProviderUpdateView, ServiceProviderDetailView, ServiceProviderDeleteView,
  ServiceProviderRepListView, ServiceProviderRepCreateView, ServiceProviderRepUpdateView, ServiceProviderRepDetailView, ServiceProviderRepDeleteView,
  LocationListView, LocationCreateView, LocationUpdateView, LocationDetailView, LocationDeleteView, ValidateLocationView,
  LocationFunctionListView, LocationFunctionCreateView, LocationFunctionUpdateView, LocationFunctionDeleteView,
  PhoneNumberListView, PhoneNumberCreateView, PhoneNumberUpdateView, PhoneNumberDetailView, PhoneNumberDeleteView, PhoneNumberBulkUpdateView,
  PhoneNumberRangeListView, PhoneNumberRangeCreateView, PhoneNumberRangeUpdateView, PhoneNumberRangeDetailView, PhoneNumberRangeDeleteView,
  UsageTypeListView, UsageTypeCreateView, UsageTypeUpdateView, UsageTypeDeleteView,
  country_list,
  generic_bulk_update, generic_bulk_delete
)
from .models import Location, ServiceProvider, CircuitDetail, PhoneNumber, PhoneNumberRange, Country, LocationFunction, ServiceProviderRep

app_name = 'telephony'

urlpatterns = [
      # Country-related URLs
    path('country_list/', country_list, name='country_list'),
    path('countries/', country_list, name='country_list'),
  
    # Location-related URLs
    path('location/', LocationListView.as_view(), name='location'),
    path('location/new/', LocationCreateView.as_view(), name='location_new'),
    path('location/<int:pk>/edit/', LocationUpdateView.as_view(), name='location_edit'),
    path('location/<int:pk>/details/', LocationDetailView.as_view(), name='location_details'),
    path('location/<int:pk>/delete/', LocationDeleteView.as_view(), name='location_delete'),
    path('location/<int:pk>/validate/', ValidateLocationView.as_view(), name='validate_location'),
    path('location/batch_edit/', generic_bulk_update, {'model_class': Location}, name='location_batch_edit'),
    path('location/batch_delete/', generic_bulk_delete, {'model_class': Location}, name='location_batch_delete'),

    #Location-Function/Purpose URLs
    path('location_function/', LocationFunctionListView.as_view(), name='location_function'),
    path('location_function/new/', LocationFunctionCreateView.as_view(), name='location_function_new'),
    path('location_function/<int:pk>/edit/', LocationFunctionUpdateView.as_view(), name='location_function_edit'),
    path('location_function/<int:pk>/delete/', LocationFunctionDeleteView.as_view(), name='location_function_delete'),
    
    # Service provider-related URLs
    path('service_provider/', ServiceProviderListView.as_view(), name='service_provider'),
    path('service_provider/new/', ServiceProviderCreateView.as_view(), name='service_provider_new'),
    path('service_provider/<int:pk>/edit/', ServiceProviderUpdateView.as_view(), name='service_provider_edit'),
    path('service_provider/<int:pk>/details/', ServiceProviderDetailView.as_view(), name='service_provider_get'),
    path('service_provider/<int:pk>/delete/', ServiceProviderDeleteView.as_view(), name='service_provider_delete'),
    
    # Service provider rep-related URLs
    path('service_provider_rep/', ServiceProviderRepListView.as_view(), name='service_provider_rep'),
    path('service_provider_rep/new/', ServiceProviderRepCreateView.as_view(), name='service_provider_rep_new'),
    path('service_provider_rep/<int:pk>/edit', ServiceProviderRepUpdateView.as_view(), name='service_provider_rep_edit'),
    path('service_provider_rep/<int:pk>/delete/', ServiceProviderRepDeleteView.as_view(), name='service_provider_rep_delete'),
   
    # Circuit-related URL
    # path('circuits/', views.circuits, name='circuits'),

    # Phone number-related URLs
    path('phone_number/', PhoneNumberListView.as_view(), name='phone_number'),
    path('phone_number/new/', PhoneNumberCreateView.as_view(), name='phone_number_new'),
    path('phone_number/<int:pk>/edit/', PhoneNumberUpdateView.as_view(), name='phone_number_edit'),
    path('phone_number/<int:pk>/details/', PhoneNumberDetailView.as_view(), name='phone_number_details'),
    path('phone_number/<int:pk>/delete/', PhoneNumberDeleteView.as_view(), name='phone_number_delete'),
    path('phone_number/batch_edit/', generic_bulk_update, {'model_class': PhoneNumber}, name='phone_number_batch_edit'),
    path('phone_number/batch_delete/', generic_bulk_delete, {'model_class': PhoneNumber}, name='phone_number_batch_delete'),
    path('phone_number_bulk_update/', PhoneNumberBulkUpdateView.as_view(), name='phone_number_bulk_update'),

    # Phone Number Range-related URLs
    path('phone_number_range/', PhoneNumberRangeListView.as_view(), name='phone_number_range'),
    path('phone_number_range/new/', PhoneNumberRangeCreateView.as_view(), name='phone_number_range_new'),
    path('phone_number_range/<int:pk>/edit/', PhoneNumberRangeUpdateView.as_view(), name='phone_number_range_edit'),
    path('phone_number_range/<int:pk>/details/', PhoneNumberRangeDetailView.as_view(), name='phone_number_range_details'),
    path('phone_number_range/<int:pk>/delete/', PhoneNumberRangeDeleteView.as_view(), name='phone_number_range_delete'),
    
   #Usage Type URLs
    path('usage_type/', UsageTypeListView.as_view(), name='usage_type'),
    path('usage_type/new/', UsageTypeCreateView.as_view(), name='usage_type_new'),
    path('usage_type/<int:pk>/edit/', UsageTypeUpdateView.as_view(), name='usage_type_edit'),
    path('usage_type/<int:pk>/delete/', UsageTypeDeleteView.as_view(), name='usage_type_delete'),

]

