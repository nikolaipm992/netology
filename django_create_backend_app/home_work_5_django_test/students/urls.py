# students/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoursesViewSet

router = DefaultRouter()
router.register(r'courses', CoursesViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
]