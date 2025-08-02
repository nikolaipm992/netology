# advertisements/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользователь может редактировать/удалять объявление только, если он его автор.
    Для всех остальных разрешены только безопасные методы (чтение).
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем запись только владельцу объявления
        return obj.creator == request.user


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Пользователь может редактировать/удалять объявление, если он его автор ИЛИ если он админ (is_staff).
    Для всех остальных разрешены только безопасные методы (чтение).
    Это реализует дополнительное задание "Права для админов".
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем запись владельцу объявления ИЛИ админу
        return obj.creator == request.user or request.user.is_staff


# TODO: реализуйте необходимые permissions-классы
# Подсказка: используйте IsAuthenticatedOrReadOnly и IsOwnerOrReadOnly
# (последний нужно реализовать)
# 
# Реализация: 
# 1. IsOwnerOrReadOnly реализован для контроля доступа к отдельным объектам 
#    (обновление/удаление только владельцем).
# 2. IsOwnerOrAdminOrReadOnly реализован как расширение, позволяющее админам
#    также управлять любыми объектами (дополнительное задание).
# 3. IsAuthenticatedOrReadOnly (встроенный класс DRF) должен использоваться
#    во ViewSet для контроля создания (create), чтобы только аутентифицированные
#    пользователи могли создавать объявления.