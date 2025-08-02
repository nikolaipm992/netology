# students/serializers.py
from rest_framework import serializers
from .models import Course, Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    # Если вы хотите включить студентов в сериализацию курса:
    # students = StudentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = '__all__'