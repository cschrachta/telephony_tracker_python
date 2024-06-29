from django.urls import path
from . import views

urlpatterns = [
  path("", views.index, name="index"),
  path('locations/', views.locations, name='locations'),
  #path('locations/', views.location_list, name='location_list'),
  path('locations/<int:location_id>/', views.get_location, name='get_location'),
  path('verify_location/<int:location_id>/', views.verify_location, name='verify_location'),
  path('delete_location/', views.delete_location, name='delete_location'),
  path('service_provider/', views.service_providers, name='service_provider'),
  path('circuits/', views.circuits, name='circuits'),
  path('phone_numbers/', views.phone_numbers, name='phone_numbers'),
  path('country_list/', views.country_list, name='country_list'),
  path('countries/', views.country_list, name='country_list'),
]
