# update_countries.py

import requests
from django.core.management.base import BaseCommand
from telephony.models import Country

class Command(BaseCommand):
    help = 'Updates the countries table with data from a REST Countries public source API'

    def handle(self, *args, **kwargs):
        url = 'https://restcountries.com/v3.1/all'
        response = requests.get(url)
        if response.status_code == 200:
            countries_data = response.json()
            for country_data in countries_data:
                name = country_data.get('name', {}).get('common')
                iso2_code = country_data.get('cca2')
                iso3_code = country_data.get('cca3')
                calling_codes = country_data.get('idd', {})
                e164_root = calling_codes.get('root', '')
                e164_suffixes = calling_codes.get('suffixes', [])
                region = country_data.get('region', '')
                subregion = country_data.get('subregion', '')
                capital = country_data.get('capital', [None])[0]
                if capital is None:
                    capital = "N/A"  # Default value for missing capital
                if e164_root == '+1':
                    e164_code = e164_root
                elif e164_root and e164_suffixes:
                    e164_code = f"{e164_root}{e164_suffixes[0]}"
                else:
                    e164_code = None
                flag = country_data.get('flags', {})
                flag_png_url = flag.get('png')
                flag_svg_url = flag.get('svg')
                flag_alt_description = flag.get('alt')
                postal_code_data = country_data.get('postalCode', {})
                postal_code_format = postal_code_data.get('format', '')
                postal_code_regex = postal_code_data.get('regex', '')
                country, created = Country.objects.update_or_create(
                    name=country_data['name']['common'],
                    defaults={
                        'iso2_code': iso2_code,
                        'iso3_code': iso3_code,
                        'e164_code': e164_code,
                        'capital': capital,
                        'region': region,
                        'subregion': subregion,
                        'population': country_data.get('population', 0),
                        'area': country_data.get('area', 0),
                        'flag_png_url': flag_png_url,
                        'flag_svg_url': flag_svg_url,
                        'flag_alt_description': flag_alt_description,
                        'postal_code_format': postal_code_format,
                        'postal_code_regex': postal_code_regex,
                    }
                
                )
            self.stdout.write(self.style.SUCCESS('Successfully updated countries'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch data'))
