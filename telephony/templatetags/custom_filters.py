# telephony/templatetags/custom_filters.py
from django import template
import django_filters
from django.urls import reverse_lazy, reverse
from telephony.models import Location, ServiceProvider, CircuitDetail, PhoneNumber, Country, UsageType, PhoneNumberRange

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

@register.filter(name='get_nested_item')
def get_nested_item(dict_obj, key):
    keys = key.split('.')
    for k in keys:
        dict_obj = dict_obj.get(k, None)
        if dict_obj is None:
            break
    return dict_obj

@register.filter(name='get_url')
def get_url(item, field_name):
    url_name = {
        'directory_number': 'telephony:phone_number_edit',
        'service_provider': 'telephony:service_provider_edit',
        'location': 'telephony:location_edit',
    }.get(field_name)

    if url_name:
        return reverse_lazy(url_name, args=[getattr(item, 'id', None) or getattr(item, field_name).id])
    return None
