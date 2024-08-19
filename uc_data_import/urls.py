from django.urls import path
from . import views

app_name = 'uc_data_import'

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('success/', views.success, name='success'),
]