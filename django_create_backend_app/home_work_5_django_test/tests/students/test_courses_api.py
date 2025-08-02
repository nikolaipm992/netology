# tests/students/test_courses_api.py
import pytest
from django.urls import reverse
from rest_framework import status
# Предполагаем, что модели находятся в students/models.py
# from students.models import Course

def print_all_url_names():
    resolver = get_resolver()
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'name') and pattern.name:
            print(pattern.name)
        if hasattr(pattern, 'url_patterns'):
            for sub_pattern in pattern.url_patterns:
                if hasattr(sub_pattern, 'name') and sub_pattern.name:
                    print(f"  {sub_pattern.name}")
# --- Тест: Получение одного курса (retrieve) ---
@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
    """Проверка получения первого курса (retrieve-логика)."""
    # 1. Создаем курс через фабрику
    course = course_factory(name="Тестовый курс")

    # 2. Строим URL и делаем запрос через тестовый клиент
    url = reverse('course-detail', args=[course.id])
    response = api_client.get(url)

    # 3. Проверяем, что вернулся код 200 OK
    assert response.status_code == status.HTTP_200_OK

    # 4. Проверяем, что вернулся именно тот курс, который запрашивали
    data = response.json()
    assert data['id'] == course.id
    assert data['name'] == course.name


# --- Тест: Получение списка курсов (list) ---
@pytest.mark.django_db
def test_list_courses(api_client, course_factory):
    """Проверка получения списка курсов (list-логика)."""
    # 1. Создаем несколько курсов через фабрику
    courses = course_factory(_quantity=3)

    # 2. Строим URL и делаем запрос
    url = reverse('course-list')
    response = api_client.get(url)

    # 3. Проверяем код 200 OK
    assert response.status_code == status.HTTP_200_OK

    # 4. Проверяем результат
    data = response.json()
    assert len(data) == 3
    # Проверяем, что ID курсов в ответе совпадают с созданными
    returned_ids = {item['id'] for item in data}
    created_ids = {course.id for course in courses}
    assert returned_ids == created_ids


# --- Тест: Фильтрация списка курсов по `id` ---
@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    """Проверка фильтрации списка курсов по `id`."""
    # 1. Создаем курсы
    course1 = course_factory(name="Курс 1")
    course2 = course_factory(name="Курс 2")
    course3 = course_factory(name="Курс 3")

    # 2. Передаем ID одного курса в фильтр
    url = reverse('course-list')
    # Используем аргумент `data` для передачи GET-параметров
    response = api_client.get(url, {'id': course2.id})

    # 3. Проверяем результат запроса с фильтром
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == course2.id
    assert data[0]['name'] == course2.name


# --- Тест: Фильтрация списка курсов по `name` ---
@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    """Проверка фильтрации списка курсов по `name`."""
    # 1. Создаем курсы
    course1 = course_factory(name="Курс Python")
    course2 = course_factory(name="Курс Java")
    course3 = course_factory(name="Курс Python") # Еще один с тем же именем

    # 2. Фильтруем по имени
    url = reverse('course-list')
    response = api_client.get(url, {'name': course1.name})

    # 3. Проверяем результат
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2 # Должно найти 2 курса с именем "Курс Python"
    returned_names = [item['name'] for item in data]
    assert all(name == course1.name for name in returned_names)


# --- Тест: Успешное создание курса ---
@pytest.mark.django_db
def test_create_course(api_client):
    """Тест успешного создания курса."""
    # 1. Готовим JSON-данные
    url = reverse('course-list')
    data = {
        'name': 'Новый курс',
        # Добавьте другие обязательные поля модели Course, если они есть
    }

    # 2. Создаём курс
    response = api_client.post(url, data, format='json')

    # 3. Проверяем код 201 Created
    assert response.status_code == status.HTTP_201_CREATED

    # 4. Проверяем, что курс действительно создан в БД
    from students.models import Course # Импорт внутри теста для надежности
    assert Course.objects.filter(name=data['name']).exists()


# --- Тест: Успешное обновление курса ---
@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    """Тест успешного обновления курса."""
    # 1. Сначала через фабрику создаём курс
    course = course_factory(name="Старое имя курса")

    # 2. Потом обновляем JSON-данными
    url = reverse