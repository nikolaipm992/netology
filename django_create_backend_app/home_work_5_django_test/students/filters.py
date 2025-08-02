# students/filters.py
import django_filters
from .models import Course

class CourseFilter(django_filters.FilterSet):
    class Meta:
        model = Course
        fields = {
            'name': ['exact', 'icontains'],  # Пример фильтрации по имени
            'id': ['exact'],  # Фильтрация по ID
        }