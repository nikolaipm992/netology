# advertisements/serializers.py
from rest_framework import serializers
from .models import Advertisement, AdvertisementStatusChoices

class AdvertisementSerializer(serializers.ModelSerializer):
    # Поле creator будет отображаться как строка (имя пользователя)
    # read_only=True гарантирует, что клиент не может его изменить
    creator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Advertisement
        # Явно перечисляем поля вместо '__all__'
        # '__all__' может быть небезопасно и менее читаемо
        fields = [
            'id', 'title', 'description', 'status', 'creator',
            'created_at', 'updated_at'
        ]
        # Либо можно использовать fields = '__all__' и read_only_fields
        # fields = '__all__'
        # read_only_fields = ('id', 'creator', 'created_at', 'updated_at')

    def validate(self, data):
        """
        Проверка, что у пользователя не больше 10 открытых объявлений.
        Эта валидация выполняется как при создании, так и при обновлении.
        """
        # Получаем текущего пользователя из контекста запроса
        user = self.context['request'].user
        # Получаем экземпляр редактируемого объекта (если это обновление)
        instance = getattr(self, 'instance', None)

        # Определяем новый статус. Если поле status не передано (PATCH),
        # берем его из существующего экземпляра или используем значение по умолчанию.
        new_status = data.get('status', instance.status if instance else AdvertisementStatusChoices.OPEN)

        # Если новое объявление не будет в статусе OPEN, валидация не требуется
        if new_status != AdvertisementStatusChoices.OPEN:
            return data # Возвращаем данные без дополнительной проверки

        # Считаем количество уже существующих открытых объявлений для этого пользователя
        open_ads_queryset = Advertisement.objects.filter(
            creator=user,
            status=AdvertisementStatusChoices.OPEN
        )
        # При обновлении исключаем текущий экземпляр из подсчета,
        # чтобы не считать его дважды
        if instance:
            open_ads_queryset = open_ads_queryset.exclude(pk=instance.pk)

        open_ads_count = open_ads_queryset.count()

        # Проверяем лимит
        if open_ads_count >= 10:
            raise serializers.ValidationError(
                "Пользователь не может иметь более 10 открытых объявлений."
            )

        return data

    # TODO: добавьте валидацию на максимальное количество открытых объявлений (status=OPEN) для одного пользователя
    # Проверка должна происходить либо в методе validate, либо в validate_status
    # (в зависимости от того, где удобнее). При проверке учитывайте, что при PATCH-запросе
    # некоторые поля могут не передаваться
    # 
    # Реализация: Валидация реализована в методе `validate`, так как она требует
    # доступа как к новым данным (data), так и к контексту (пользователь, instance).
    # Метод `validate_status` менее удобен, так как он проверяет только одно поле
    # и не имеет прямого доступа к другим полям или контексту запроса для подсчета
    # существующих объявлений.