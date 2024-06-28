# telephony/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='toggle_order')
def toggle_order(order, sort_by, current_sort_by):
    if sort_by == current_sort_by:
        return 'desc' if order == 'asc' else 'asc'
    return 'asc'