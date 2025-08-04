# students/serializers.py
from rest_framework import serializers
from django.conf import settings
from .models import Course, Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    # Уточни поле students в соответствии с тем, как оно должно отображаться
    # students = StudentSerializer(many=True, read_only=True) # Только для чтения
    # Или, если нужно редактировать:
    students = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), many=True, required=False
    )

    class Meta:
        model = Course
        fields = '__all__'

    def validate_students(self, value):
        """Проверка максимального количества студентов."""
        # Получаем значение из настроек, по умолчанию 20
        max_students = getattr(settings, 'MAX_STUDENTS_PER_COURSE', 20)
        if len(value) > max_students:
            raise serializers.ValidationError(
                f"На курсе не может быть больше {max_students} студентов."
            )
        return value