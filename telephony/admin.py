from django.contrib import admin
from .models import Country, Location, UsageType, ServiceProvider, ServiceProviderRep, SwitchType, ConnectionType, CircuitDetail, PhoneNumber, PhoneNumberRange
from .forms import PhoneNumberRangeForm

def populate_phone_numbers(modeladmin, request, queryset):
    for number_range in queryset:
        start = number_range.start_number
        end = number_range.end_number if number_range.end_number else start
        country_code = number_range.country.e164_code
        circuit = number_range.circuitdetail.circuit_number
        for number in range(start, end + 1):
            PhoneNumber.objects.update_or_create(
                directory_number=number,
                defaults={
                    'country_code': country_code,  # Populate as necessary
                    'region_code': None,  # Populate as necessary
                    'subscriber_number': number,
                    'service_location': number_range.location,
                    'phone_number_range': number_range,
                    'usage_type': number_range.usage_type,
                    'service_provider': number_range.service_provider,
                    'circuit': number_range.circuit,
                }
            )
    modeladmin.message_user(request, "Phone numbers populated successfully from the selected ranges.")

populate_phone_numbers.short_description = "Populate phone numbers from selected ranges"

class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ['directory_number', 'service_location', 'circuit', 'is_active']
    form = PhoneNumberRangeForm

class PhoneNumberRangeAdmin(admin.ModelAdmin):
    list_display = ['start_number', 'end_number', 'service_provider', 'location', 'circuit']
    actions = [populate_phone_numbers]
    form = PhoneNumberRangeForm


# Register your models here.

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    ordering = ['name']  # Sort by 'name' field in the admin


#admin.site.register(Country)
admin.site.register(Location)
admin.site.register(UsageType)
admin.site.register(ServiceProvider)
admin.site.register(ServiceProviderRep)
admin.site.register(SwitchType)
admin.site.register(ConnectionType)
admin.site.register(CircuitDetail)
admin.site.register(PhoneNumber)
#admin.site.register(PhoneNumberAdmin)
admin.site.register(PhoneNumberRange, PhoneNumberRangeAdmin)
