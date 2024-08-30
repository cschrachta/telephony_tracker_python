# telephony/templatetags/custom_filters.py
from django import template
import django_filters
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

