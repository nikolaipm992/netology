from django.core.management.base import BaseCommand
from phones.models import Phone
import csv


class Command(BaseCommand):
    help = 'Импорт телефонов из CSV-файла'

    def handle(self, *args, **options):
        # Удаляем старые записи (опционально)
        Phone.objects.all().delete()

        with open('../phones.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                phone = Phone(
                    id=int(row['id']),
                    name=row['name'],
                    price=row['price'],
                    image=row['image'],
                    release_date=row['release_date'],
                    lte_exists=True if row['lte_exists'].lower() == 'true' else False
                )
                phone.save()

        self.stdout.write(self.style.SUCCESS('✅ Все телефоны успешно загружены'))