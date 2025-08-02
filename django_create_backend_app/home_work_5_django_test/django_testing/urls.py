# django_testing/urls.py (или как он у вас называется)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/students/', include('students.urls')), # Путь может отличаться
    # ...другие URL...
]