import requests, re
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from telephony.models import Country

# print only countries where the match fails

class Command(BaseCommand):
    help = 'Validates E.164 codes from countrycode.org against the country data'

    def handle(self, *args, **kwargs):
        url = 'https://countrycode.org/'
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the table or relevant section that contains the E.164 codes
            table = soup.find('table')  # Adjust this selector based on the actual structure
            rows = table.find_all('tr')

            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 3:  # Ensure there are enough columns
                    country_name = columns[0].get_text(strip=True)
                    e164_code = columns[1].get_text(strip=True)
                    iso_codes = columns[2].get_text(strip=True)
                    
                    # Adjust the e164_code with a regular expression
                    e164_code_clean = f"+{re.sub(r'[^0-9]', '', e164_code)}"
                    
                    # Split the combined ISO2/ISO3 codes
                    iso2_code, iso3_code = map(str.strip, iso_codes.split('/'))

                    # Try to find the matching country in your Django model by ISO3 code
                    try:
                        country = Country.objects.get(iso3_code__iexact=iso3_code)
                        if country.e164_code != e164_code_clean:
                            self.stdout.write(self.style.WARNING(
                                f"E.164 mismatch for {country_name} (ISO3: {iso3_code}): "
                                f"Expected {country.e164_code}, Found {e164_code_clean}"
                            ))
                    except Country.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Country with ISO3 code {iso3_code} not found in the database."))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch data from countrycode.org'))


#print the analysis match for all countries 

# class Command(BaseCommand):
#     help = 'Validates E.164 codes from phonenum.info against the country data'

#     def handle(self, *args, **kwargs):
#         url = 'https://phonenum.info/en/country-code/'
#         response = requests.get(url)

#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, 'html.parser')
            
#             # Find the table or relevant section that contains the E.164 codes
#             table = soup.find('table')  # Adjust this selector based on the actual structure
#             rows = table.find_all('tr')

#             for row in rows:
#                 columns = row.find_all('td')
#                 if len(columns) >= 3:  # Ensure there are enough columns
#                     country_name = columns[1].get_text(strip=True)
#                     e164_code = columns[0].get_text(strip=True)
#                     iso3_code = columns[2].get_text(strip=True)

#                     # Try to find the matching country in your Django model by ISO3 code
#                     try:
#                         country = Country.objects.get(iso3_code__iexact=iso3_code)
#                         if country.e164_code != e164_code:
#                             self.stdout.write(self.style.WARNING(
#                                 f"E.164 mismatch for {country_name} (ISO3: {iso3_code}): "
#                                 f"Expected {country.e164_code}, Found {e164_code}"
#                             ))
#                         else:
#                             self.stdout.write(self.style.SUCCESS(f"{country_name} (ISO3: {iso3_code}) E.164 code matches."))
#                     except Country.DoesNotExist:
#                         self.stdout.write(self.style.ERROR(f"Country with ISO3 code {iso3_code} not found in the database."))
#         else:
#             self.stdout.write(self.style.ERROR('Failed to fetch data from phonenum.info'))