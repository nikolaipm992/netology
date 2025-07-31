from django.urls import path
from . import views

app_name = 'phones'

urlpatterns = [
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<slug:slug>/', views.phone, name='phone'),
]