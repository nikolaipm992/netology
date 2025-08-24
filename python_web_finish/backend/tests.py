# backend/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Category, Shop, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact

User = get_user_model()

class ShopAPITestCase(TestCase):
    """Тесты для API магазинов и категорий"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = APIClient()

        self.supplier_user = User.objects.create_user(
            email='supplier@example.com',
            password='suppliertestpass123',
            first_name='Test',
            last_name='Supplier',
            company='Supplier Company',
            position='Manager',
            type='shop'
        )
        self.supplier_user.is_supplier = True
        self.supplier_user.save()

        self.shop = Shop.objects.create(
            name='Test Shop',
            url='http://testshop.com',
            user=self.supplier_user,
            state=True
        )

        self.category = Category.objects.create(name='Test Category')
        self.category.shops.add(self.shop)

        self.product = Product.objects.create(
            name='Test Product',
            category=self.category
        )

        self.product_info = ProductInfo.objects.create(
            model='TP-123',
            external_id=1,
            product=self.product,
            shop=self.shop,
            quantity=10,
            price=1000,
            price_rrc=1200
        )

        self.parameter = Parameter.objects.create(name='Color')
        self.product_parameter = ProductParameter.objects.create(
            product_info=self.product_info,
            parameter=self.parameter,
            value='Red'
        )

    def test_get_categories(self):
        """Тест получения списка категорий"""
        response = self.client.get(reverse('backend:categories'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Category')

    def test_get_shops(self):
        """Тест получения списка активных магазинов"""
        response = self.client.get(reverse('backend:shops'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Shop')

    def test_get_products(self):
        """Тест получения списка товаров"""
        response = self.client.get(reverse('backend:products'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        product_data = response.data[0]
        self.assertEqual(product_data['model'], 'TP-123')
        self.assertEqual(product_data['price'], 1000)

    def test_get_products_with_filters(self):
        """Тест получения списка товаров с фильтрами"""
        response = self.client.get(f"{reverse('backend:products')}?shop_id={self.shop.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['shop'], self.shop.id)

        response = self.client.get(f"{reverse('backend:products')}?category_id={self.category.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product'], self.product.id)
        self.assertEqual(response.data[0]['shop'], self.shop.id)


class UserAPITestCase(TestCase):
    """Тесты для API регистрации и аутентификации пользователей"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = APIClient()
        self.register_url = reverse('backend:user-register')
        self.login_url = reverse('backend:user-login')

    def test_user_registration(self):
        """Тест регистрации нового пользователя"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'company': 'Test Corp',
            'position': 'Developer'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['Status'])
        self.assertTrue(User.objects.filter(email='john.doe@example.com').exists())

    def test_user_registration_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
            'company': 'Test Corp',
            'position': 'Developer'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['Status'])

    def test_user_login(self):
        """Тест аутентификации пользователя"""
        user = User.objects.create_user(
            email='testlogin@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Login'
        )
        user.is_active = True
        user.save()
        
        data = {
            'email': 'testlogin@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['Status'])
        self.assertIn('Token', response.data)


class OrderAPITestCase(TestCase):
    """Тесты для API работы с заказами и корзиной"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='orderuser@example.com',
            password='ordertestpass123',
            first_name='Order',
            last_name='User'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.supplier_user = User.objects.create_user(
            email='supplier2@example.com',
            password='suppliertestpass123',
            type='shop'
        )
        self.supplier_user.is_supplier = True
        self.supplier_user.save()
        
        self.shop = Shop.objects.create(
            name='Order Test Shop',
            user=self.supplier_user,
            state=True
        )
        
        self.category = Category.objects.create(name='Order Test Category')
        self.category.shops.add(self.shop)
        
        self.product = Product.objects.create(
            name='Order Test Product',
            category=self.category
        )
        
        self.product_info = ProductInfo.objects.create(
            model='OTP-456',
            external_id=2,
            product=self.product,
            shop=self.shop,
            quantity=5,
            price=500,
            price_rrc=600
        )

        self.contact = Contact.objects.create(
            user=self.user,
            city='Test City',
            street='Test Street',
            house='1',
            phone='+79998887766'
        )

    def test_add_to_basket(self):
        """Тест добавления товара в корзину"""
        data = {
            'items': [
                {
                    'product_info': self.product_info.id,
                    'quantity': 2
                }
            ]
        }
        response = self.client.post(reverse('backend:basket'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['Status'])

        basket = Order.objects.get(user=self.user, state='basket')
        self.assertEqual(basket.ordered_items.count(), 1)
        self.assertEqual(basket.ordered_items.first().quantity, 2)

    def test_get_basket(self):
        """Тест получения содержимого корзины"""
        OrderItem.objects.create(
            order=Order.objects.get_or_create(user=self.user, state='basket')[0],
            product_info=self.product_info,
            quantity=1
        )
        
        response = self.client.get(reverse('backend:basket'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('ordered_items', [])), 1)
        if response.data.get('ordered_items'):
            self.assertEqual(response.data['ordered_items'][0]['quantity'], 1)

    def test_create_order(self):
        """Тест создания заказа"""
        basket, _ = Order.objects.get_or_create(user=self.user, state='basket')
        OrderItem.objects.create(
            order=basket,
            product_info=self.product_info,
            quantity=1
        )
        
        data = {
            'contact': self.contact.id
        }
        response = self.client.post(reverse('backend:orders-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['Status'])

        basket.refresh_from_db()
        self.assertEqual(basket.state, 'new')
        self.assertEqual(basket.contact, self.contact)

    def test_get_orders(self):
        """Тест получения списка заказов пользователя"""
        order = Order.objects.create(
            user=self.user,
            state='new',
            contact=self.contact
        )
        OrderItem.objects.create(
            order=order,
            product_info=self.product_info,
            quantity=1
        )
        
        response = self.client.get(reverse('backend:orders-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        found_order = False
        for order_data in response.data:
            if order_data.get('state') == 'new':
                found_order = True
                break
        self.assertTrue(found_order, "Заказ со статусом 'new' не найден в ответе")


class ContactAPITestCase(TestCase):
    """Тесты для API работы с контактами пользователя"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            email='contactuser@example.com',
            password='contacttestpass123',
            first_name='Contact',
            last_name='User'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_contact(self):
        """Тест создания нового контакта"""
        data = {
            'city': 'Contact City',
            'street': 'Contact Street',
            'house': '10',
            'phone': '+79991112233'
        }
        response = self.client.post(reverse('backend:user-contacts'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['city'], 'Contact City')
        self.assertTrue(Contact.objects.filter(user=self.user, city='Contact City').exists())

    def test_get_contacts(self):
        """Тест получения списка контактов пользователя"""
        Contact.objects.create(
            user=self.user,
            city='Get City',
            street='Get Street',
            house='5',
            phone='+79994445566'
        )
        
        response = self.client.get(reverse('backend:user-contacts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['city'], 'Get City')
