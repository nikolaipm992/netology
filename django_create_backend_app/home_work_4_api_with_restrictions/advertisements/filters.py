# advertisements/filters.py
import django_filters
from django_filters import DateFromToRangeFilter, ChoiceFilter, ModelChoiceFilter
from .models import Advertisement, AdvertisementStatusChoices

class AdvertisementFilter(django_filters.FilterSet):
    # Явно определяем фильтр по дате создания с использованием DateFromToRangeFilter
    # как указано в задании.
    created_at = DateFromToRangeFilter()

    # Фильтр по статусу. Можно использовать ChoiceFilter, если AdvertisementStatusChoices
    # это простой Enum/Choices. ModelChoiceFilter если это отдельная модель.
    # В данном случае, предположим, что это Choices.
    # status = ChoiceFilter(choices=AdvertisementStatusChoices.choices) # Альтернатива 1
    # Или просто укажем в Meta.fields, если хотим стандартное поведение.

    class Meta:
        model = Advertisement
        # Указываем поля для автоматической фильтрации.
        # created_at НЕ указываем здесь, потому что он уже определен явно выше.
        # Это предотвращает дублирование.
        fields = {
            'status': ['exact'],  # Создаст фильтр status (status__exact)
            'creator': ['exact'], # Создаст фильтр creator (creator__exact)
            # 'created_at' НЕ указываем, т.к. он уже определен явно как DateFromToRangeFilter
            # 'title': ['icontains'], # Пример, если нужна фильтрация по названию
        }

    # TODO: задайте поля для фильтрации. помните, что некоторые поля в модели уже имеют фильтрацию,
    # и это нужно учесть в Meta.fields, чтобы не было дублирования
    # Например, если вы определили created_at = DateFromToRangeFilter() выше,
    # то не нужно указывать 'created_at' в fields = {...} словаре.