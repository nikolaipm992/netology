from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Advertisement
from .serializers import AdvertisementSerializer
from .filters import AdvertisementFilter
from .permissions import IsOwnerOrReadOnly  # Импортируем кастомное разрешение
# Если реализован IsOwnerOrAdminOrReadOnly, то нужно его тоже импортировать:
# from .permissions import IsOwnerOrReadOnly, IsOwnerOrAdminOrReadOnly

class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter

    def get_permissions(self):
        """Определяем права доступа для разных действий."""
        if self.action in ['list', 'retrieve']:  # Исправлено: используем in для проверки
            # Для просмотра списка и отдельного объявления
            # разрешаем всем (аутентифицированным и анонимным)
            permission_classes = []  # или [permissions.AllowAny] если нужно явно
        elif self.action == 'create':
            # Для создания нужно быть аутентифицированным
            permission_classes = [permissions.IsAuthenticated]  # Используем permissions.
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Для обновления и удаления нужно быть владельцем
            # Используем наш кастомный класс
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]  # Используем permissions.
            # Если реализован IsOwnerOrAdminOrReadOnly и вы хотите давать права админам:
            # permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]
        else:
            # Для любых других действий (например, кастомных @action)
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Автоматически устанавливаем создателя текущим пользователем
        serializer.save(creator=self.request.user)

    # TODO: реализуйте permission-классы для безопасного доступа к данным
    # (пользователь может менять и удалять только свои объявления)
    # Подсказка: IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    # (последний нужно реализовать)
    # Также не забудьте реализовать валидацию на максимальное количество открытых объявлений
    # для одного пользователя (в serializers.py или views.py)
    # 
    # Реализация: 
    # 1. IsOwnerOrReadOnly реализован в permissions.py
    # 2. Валидация количества открытых объявлений реализована в serializers.py
    # 3. get_permissions корректно назначает права доступа для разных действий