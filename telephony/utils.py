import googlemaps
from django.conf import settings

gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)

def validate_address(address):
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        # If the address is valid, return the formatted address and True
        return geocode_result[0]['formatted_address'], True
    return None, False