# students/views.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from students.filters import CourseFilter
from students.models import Course
from students.serializers import CourseSerializer


class CoursesViewSet(ModelViewSet):
    queryset = Course.objects.all()  # Убедитесь, что это есть
    serializer_class = CourseSerializer  # Убедитесь, что это есть
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CourseFilter