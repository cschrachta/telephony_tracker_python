"""
URL configuration for telephony_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

# path("", include("telephony.urls")),
# path("", include("uc_data_import.urls")),
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from telephony import views as telephony_views
from uc_data_import import views as uc_data_import_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", telephony_views.index, name="index"),
    path('telephony/', include('telephony.urls', namespace='telephony')),
    path('uc_data_import/', include('uc_data_import.urls', namespace='uc_data_import')),    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
