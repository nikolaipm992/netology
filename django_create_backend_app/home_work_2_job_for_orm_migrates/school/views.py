from django.shortcuts import render
from .models import Student

def students_list(request):
    template = 'school/students_list.html'
    
    # Используем prefetch_related для оптимизации запросов к ManyToManyField
    # и order_by для упорядочивания по группе
    students = Student.objects.prefetch_related('teachers').order_by('group')
    
    context = {
        'students': students
    }

    # используйте этот параметр для упорядочивания результатов
    # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by
    ordering = 'group'

    return render(request, template, context)