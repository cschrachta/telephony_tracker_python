# telephony/templatetags/custom_filters.py
from django import template
import django_filters
from django.urls import reverse_lazy, reverse
from telephony.models import Location, ServiceProvider, CircuitDetail, PhoneNumber, Country, UsageType, PhoneNumberRange
from django.utils.safestring import mark_safe

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

@register.simple_tag
def info_icon(tooltip_text):
    return mark_safe(f'''
    <span class="bi bi-info-circle" data-bs-toggle="tooltip" title="{tooltip_text}">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle" viewBox="0 0 16 16">
            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
            <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0"/>
        </svg>
    </span>
    ''')

@register.simple_tag
def google_maps_link(latitude, longitude, address):
    if latitude and longitude:
        return f"https://www.google.com/maps?q={latitude},{longitude}"
    elif address:
        return f"https://www.google.com/maps/search/?api=1&query={address}"
    return "#"

