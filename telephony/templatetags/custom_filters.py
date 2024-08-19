# telephony/templatetags/custom_filters.py
from django import template
import django_filters
from ..models import Location, ServiceProvider, CircuitDetail, PhoneNumber, Country, UsageType, PhoneNumberRange

register = template.Library()

@register.filter(name='toggle_order')
def toggle_order(order, sort_by, current_sort_by):
    if sort_by == current_sort_by:
        return 'desc' if order == 'asc' else 'asc'
    return 'asc'

@register.filter(name='get_attr')
def get_attr(obj, attr_name):
    """Gets an attribute of an object dynamically"""
    return getattr(obj, attr_name, None)

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})

class PhoneNumberFilter(django_filters.FilterSet):
    directory_number = django_filters.CharFilter(lookup_expr='icontains', label='Directory Number')
    assigned_to = django_filters.CharFilter(lookup_expr='icontains', label='Assigned To')
    usage_type = django_filters.ModelChoiceFilter(queryset=UsageType.objects.all(), label='Usage Type')
    service_location = django_filters.ModelChoiceFilter(queryset=Location.objects.all(), label='Service Location')
    phone_number_range = django_filters.ModelChoiceFilter(queryset=PhoneNumberRange.objects.all(), label='Phone Number Range')
    notes = django_filters.CharFilter(lookup_expr='icontains', label='Notes')
    class Meta:
        model = PhoneNumber
        fields = ['directory_number', 'service_location', 'assigned_to', 'usage_type']
