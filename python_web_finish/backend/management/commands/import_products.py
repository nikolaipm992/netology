from django.core.management.base import BaseCommand
from django.db import transaction
import yaml
import os
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

class Command(BaseCommand):
    help = 'Импорт товаров из YAML файла'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к YAML файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден'))
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при чтении файла: {e}'))
            return

        try:
            with transaction.atomic():
                shop, created = Shop.objects.get_or_create(
                    name=data['shop'],
                    defaults={'url': data.get('url', '')}
                )
                if created:
                    self.stdout.write(f'Создан магазин: {shop.name}')
                else:
                    self.stdout.write(f'Магазин {shop.name} уже существует')

                for category_name in data['categories']:
                    category, created = Category.objects.get_or_create(name=category_name)
                    if created:
                        self.stdout.write(f'Создана категория: {category_name}')
                    category.shops.add(shop)

                for item in data['goods']:
                    category, _ = Category.objects.get_or_create(name=item['category'])
                    
                    product, created = Product.objects.get_or_create(
                        name=item['name'],
                        category=category
                    )
                    if created:
                        self.stdout.write(f'Создан продукт: {item["name"]}')

                    product_info, created = ProductInfo.objects.update_or_create(
                        external_id=item['id'],
                        shop=shop,
                        product=product,
                        defaults={
                            'model': item.get('model', ''),
                            'quantity': item['quantity'],
                            'price': item['price'],
                            'price_rrc': item['price_rrc']
                        }
                    )
                    if created:
                        self.stdout.write(f'Создана информация о продукте: {item["name"]}')

                    for param_name, param_value in item.get('parameters', {}).items():
                        parameter, param_created = Parameter.objects.get_or_create(name=param_name)
                        if param_created:
                            self.stdout.write(f'Создан параметр: {param_name}')
                        
                        ProductParameter.objects.update_or_create(
                            product_info=product_info,
                            parameter=parameter,
                            defaults={'value': str(param_value)}
                        )

                self.stdout.write(
                    self.style.SUCCESS(f'Успешно импортированы товары из {file_path}')
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при импорте: {e}'))