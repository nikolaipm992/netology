# tests/students/test_courses_api.py
# ... (все предыдущие импорты и тесты) ...

# --- Дополнительные тесты ---
import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_retrieve_nonexistent_course(api_client):
    """Проверка получения несуществующего курса."""
    url = reverse('course-detail', args=[999999])  # ID, которого точно нет
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_course_without_name(api_client):
    """Тест создания курса без обязательного поля name."""
    url = reverse('course-list')
    data = {
        # Не передаем имя курса
        'description': 'Курс без названия'
    }
    
    response = api_client.post(url, data, format='json')
    
    # Ожидаем ошибку валидации
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_nonexistent_course(api_client):
    """Тест обновления несуществующего курса."""
    url = reverse('course-detail', args=[999999])  # ID, которого точно нет
    data = {
        'name': 'Обновленное название'
    }
    
    response = api_client.patch(url, data, format='json')
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_nonexistent_course(api_client):
    """Тест удаления несуществующего курса."""
    url = reverse('course-detail', args=[999999])  # ID, которого точно нет
    response = api_client.delete(url)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_empty_courses_list(api_client):
    """Проверка получения пустого списка курсов."""
    url = reverse('course-list')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == []  # Пустой список


@pytest.mark.django_db
def test_create_course_with_students(api_client, student_factory):
    """Тест создания курса с привязанными студентами."""
    # Создаем студентов
    student1 = student_factory(name="Иван Иванов")
    student2 = student_factory(name="Петр Петров")
    
    url = reverse('course-list')
    data = {
        'name': 'Новый курс',
        'students': [student1.id, student2.id]
    }
    
    response = api_client.post(url, data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    data_response = response.json()
    assert data_response['name'] == 'Новый курс'
    # assert len(data_response.get('students', [])) == 2
