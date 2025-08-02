# advertisements/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdvertisementViewSet

# Создаем router и регистрируем ViewSet
router = DefaultRouter()
router.register(r'advertisements', AdvertisementViewSet)

# URL-паттерны определяются автоматически router'ом
urlpatterns = [
    path('', include(router.urls)),
]