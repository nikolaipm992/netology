# tests/conftest.py
import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Student, Course


@pytest.fixture
def api_client():
    """Фикстура для тестового клиента API."""
    return APIClient()


@pytest.fixture
def student_factory():
    """Фикстура для фабрики студентов."""
    def factory(**kwargs):
        return baker.make(Student, **kwargs)
    return factory


@pytest.fixture
def course_factory():
    """Фикстура для фабрики курсов."""
    def factory(**kwargs):
        return baker.make(Course, **kwargs)
    return factory