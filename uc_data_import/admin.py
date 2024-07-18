from django.contrib import admin
from .models import UCSystemFile, UCDataImport

# Register your models here.
admin.site.register(UCSystemFile)
admin.site.register(UCDataImport)