# backend/views.py
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.db import transaction
from .models import *
from .serializers import *
from .signals import new_order  # Импортируем сигнал
import logging

logger = logging.getLogger(__name__)

class RegisterAccountView(views.APIView):
    """
    Для регистрации покупателей
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Проверка обязательных параметров
        required_fields = ['first_name', 'last_name', 'email', 'password', 'password_confirm', 'company', 'position']
        if not all(field in request.data for field in required_fields):
            return Response(
                {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка пароля
        if request.data['password'] != request.data['password_confirm']:
            return Response({'Status': False, 'Errors': {'password': 'Пароли не совпадают'}},
                            status=status.HTTP_400_BAD_REQUEST)

        # Проверка существования пользователя
        if User.objects.filter(email=request.data['email']).exists():
            return Response({'Status': False, 'Errors': {'email': 'Пользователь с таким email уже существует'}},
                            status=status.HTTP_400_BAD_REQUEST)

        # Создание пользователя
        try:
            user = User.objects.create_user(
                email=request.data['email'],
                password=request.data['password'],
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                company=request.data['company'],
                position=request.data['position'],
                type='buyer' # Предполагается, что тип 'buyer' по умолчанию для регистрации
            )
            return Response({'Status': True, 'Message': 'Пользователь успешно зарегистрирован'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'Status': False, 'Errors': f'Ошибка при создании пользователя: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)


class LoginAccountView(views.APIView):
    """
    Класс для авторизации пользователей
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, email=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({'Status': True, 'Token': token.key})
                else:
                    return Response({'Status': False, 'Errors': 'Аккаунт не подтвержден'},
                                    status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'Status': False, 'Errors': 'Не удалось авторизовать. Неверный email или пароль.'},
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы (email, password)'},
                            status=status.HTTP_400_BAD_REQUEST)


class CategoryView(generics.ListAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny] # Доступно всем


class ShopView(generics.ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shop.objects.filter(state=True) # Только активные магазины
    serializer_class = ShopSerializer
    permission_classes = [AllowAny] # Доступно всем


class ProductInfoView(generics.ListAPIView):
    """
    Класс для поиска товаров/позиций (ProductInfo)
    """
    serializer_class = ProductInfoSerializer
    permission_classes = [AllowAny] # Доступно всем

    def get_queryset(self):
        queryset = ProductInfo.objects.select_related('shop', 'product__category')
        shop_id = self.request.query_params.get('shop_id', None)
        category_id = self.request.query_params.get('category_id', None)

        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        if category_id:
            queryset = queryset.filter(product__category_id=category_id)

        return queryset


class BasketView(views.APIView):
    """
    Класс для работы с корзиной пользователя
    """
    permission_classes = [IsAuthenticated] # Явно указываем

    def get(self, request, *args, **kwargs):
        """Получить содержимое корзины"""
        basket, _ = Order.objects.get_or_create(user=request.user, state='basket')
        serializer = OrderSerializer(basket)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Добавить товары в корзину"""
        items = request.data.get('items', None)
        if items:
            basket, _ = Order.objects.get_or_create(user=request.user, state='basket')
            objects_created = 0
            for item in items:
                item['order'] = basket.id # Привязываем к корзине
                serializer = OrderItemCreateSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                    objects_created += 1
                else:
                    return Response({'Status': False, 'Errors': serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
            return Response({'Status': True, 'Создано объектов': objects_created})
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы (items)'},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """Удалить товары из корзины"""
        items_str = request.data.get('items', None)
        if items_str:
            try:
                items_list = [int(item_id.strip()) for item_id in items_str.split(',')]
            except ValueError:
                return Response({'Status': False, 'Errors': 'Некорректный формат списка ID'},
                                status=status.HTTP_400_BAD_REQUEST)

            basket, _ = Order.objects.get_or_create(user=request.user, state='basket')
            # Удаляем элементы корзины, принадлежащие этой корзине и пользователю
            deleted_count, _ = OrderItem.objects.filter(order_id=basket.id, id__in=items_list).delete()
            return Response({'Status': True, 'Удалено объектов': deleted_count})
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы (items)'},
                        status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """Обновить количество товаров в корзине"""
        items = request.data.get('items', None)
        if items:
            basket, _ = Order.objects.get_or_create(user=request.user, state='basket')
            objects_updated = 0
            for item in items:
                if 'id' in item and 'quantity' in item:
                    try:
                        # Проверяем, что элемент принадлежит корзине пользователя
                        order_item = OrderItem.objects.get(id=item['id'], order_id=basket.id)
                        serializer = OrderItemUpdateSerializer(order_item, data={'quantity': item['quantity']}, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            objects_updated += 1
                        else:
                           return Response({'Status': False, 'Errors': serializer.errors},
                                           status=status.HTTP_400_BAD_REQUEST)
                    except OrderItem.DoesNotExist:
                         pass
            return Response({'Status': True, 'Обновлено объектов': objects_updated})
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы (items)'},
                        status=status.HTTP_400_BAD_REQUEST)


class ContactView(views.APIView):
    """
    Класс для работы с контактами пользователя
    """
    permission_classes = [IsAuthenticated] # Явно указываем

    def get(self, request, *args, **kwargs):
        """Получить список контактов"""
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Добавить контакт"""
        # Добавляем user_id к данным запроса
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = ContactSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderView(views.APIView):
    """
    Класс для получения заказов пользователями и создания заказа
    """
    permission_classes = [IsAuthenticated] # Явно указываем

    def get(self, request, *args, **kwargs):
        """Получение списка заказов пользователя (кроме корзины)"""
        orders = Order.objects.filter(user=request.user).exclude(state='basket').select_related('contact').prefetch_related('ordered_items__product_info')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Создание заказа из корзины"""
        # Проверка обязательных параметров
        if 'contact' not in request.data:
            return Response({'Status': False, 'Errors': 'Не указан контакт (contact)'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            contact_id = int(request.data['contact'])
            contact = Contact.objects.get(id=contact_id, user=request.user) # Убедиться, что контакт принадлежит пользователю
        except (ValueError, Contact.DoesNotExist):
            return Response({'Status': False, 'Errors': 'Контакт не найден или не принадлежит пользователю'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():  # Используем транзакцию для обеспечения целостности данных
                basket = Order.objects.select_for_update().get(user=request.user, state='basket')
                if not basket.ordered_items.exists():
                     return Response({'Status': False, 'Errors': 'Корзина пуста'},
                                     status=status.HTTP_400_BAD_REQUEST)

                # Обновляем корзину: меняем статус, привязываем контакт
                basket.state = 'new'
                basket.contact = contact
                basket.save()

                # Отправляем сигнал о новом заказе
                new_order.send(sender=self.__class__, user_id=request.user.id)

                return Response({'Status': True, 'Message': 'Заказ успешно создан'}, status=status.HTTP_201_CREATED)
        except Order.DoesNotExist:
            return Response({'Status': False, 'Errors': 'Корзина не найдена'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({'Status': False, 'Errors': f'Ошибка при создании заказа: {str(e)}'},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Добавим View для получения деталей конкретного заказа
class OrderDetailView(generics.RetrieveAPIView):
    """
    Класс для получения деталей конкретного заказа
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] # Явно указываем

    def get_queryset(self):
        # Пользователь может видеть только свои заказы
        return Order.objects.filter(user=self.request.user).exclude(state='basket').select_related('contact').prefetch_related('ordered_items__product_info')


# Добавим Views для администратора/поставщика
class SupplierOrdersView(views.APIView):
    """
    Класс для получения заказов поставщиком
    """
    permission_classes = [IsAuthenticated] # Явно указываем
    
    def get(self, request, *args, **kwargs):
        # Проверяем, что пользователь является поставщиком
        if not getattr(request.user, 'is_supplier', False):  # Более безопасная проверка
            return Response({'Status': False, 'Errors': 'Доступ запрещен'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Получаем магазин пользователя
        try:
            shop = Shop.objects.get(user=request.user)
        except Shop.DoesNotExist:
            return Response({'Status': False, 'Errors': 'Магазин не найден'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Получаем заказы, содержащие товары из этого магазина
        orders = Order.objects.filter(
            state__in=['new', 'confirmed', 'assembled'],
            ordered_items__product_info__shop=shop
        ).distinct().select_related('user', 'contact').prefetch_related('ordered_items__product_info')
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class UpdateOrderStatusView(views.APIView):
    """
    Класс для обновления статуса заказа поставщиком
    """
    permission_classes = [IsAuthenticated] # Явно указываем
    
    def patch(self, request, order_id, *args, **kwargs):
        # Проверяем, что пользователь является поставщиком
        if not getattr(request.user, 'is_supplier', False):  # Более безопасная проверка
            return Response({'Status': False, 'Errors': 'Доступ запрещен'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Получаем магазин пользователя
        try:
            shop = Shop.objects.get(user=request.user)
        except Shop.DoesNotExist:
            return Response({'Status': False, 'Errors': 'Магазин не найден'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Получаем заказ
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'Status': False, 'Errors': 'Заказ не найден'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Проверяем, что заказ содержит товары из магазина пользователя
        if not order.ordered_items.filter(product_info__shop=shop).exists():
            return Response({'Status': False, 'Errors': 'Заказ не содержит товаров вашего магазина'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Обновляем статус
        new_state = request.data.get('state')
        if new_state and new_state in dict(STATE_CHOICES).keys():
            old_state = order.state
            order.state = new_state
            order.save()
            
            # Уведомление будет отправлено сигналом post_save в модели Order
            return Response({'Status': True, 'Message': 'Статус заказа обновлен'})
        else:
            return Response({'Status': False, 'Errors': 'Некорректный статус'}, 
                          status=status.HTTP_400_BAD_REQUEST)

# (Опционально) View для запуска импорта через API
class ImportProductsView(views.APIView):
    """
    Класс для запуска импорта товаров через API (для админов/поставщиков)
    """
    permission_classes = [IsAuthenticated] # Явно указываем

    def post(self, request, *args, **kwargs):
        # Проверка прав (например, только для админов или поставщиков)
        if not (request.user.is_staff or getattr(request.user, 'is_supplier', False)):
             return Response({'Status': False, 'Errors': 'Доступ запрещен'}, 
                           status=status.HTTP_403_FORBIDDEN)

        file_path = request.data.get('file_path')
        if not file_path:
            return Response({'Status': False, 'Errors': 'Не указан путь к файлу'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Здесь должна быть логика запуска импорта
        # Для Celery это могло бы быть:
        # from .tasks import do_import
        # task = do_import.delay(file_path)
        # return Response({'Status': True, 'TaskID': task.id, 'Message': 'Импорт запущен'})
        
        # Для синхронного запуска (не рекомендуется для больших файлов):
        try:
            from django.core.management import call_command
            call_command('import_products', file_path)
            return Response({'Status': True, 'Message': 'Импорт завершен'})
        except Exception as e:
            logger.error(f"Ошибка при импорте из {file_path}: {e}")
            return Response({'Status': False, 'Errors': f'Ошибка при импорте: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)