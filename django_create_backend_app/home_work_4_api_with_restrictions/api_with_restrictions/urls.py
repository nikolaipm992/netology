# api_with_restrictions/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('advertisements.urls')),
    path('admin/', admin.site.urls),
]