import csv
from django.core.management.base import BaseCommand
from phones.models import Phone

class Command(BaseCommand):
    help = 'Import phones from CSV file'

    def handle(self, *args, **options):
        with open('phones.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                phone = Phone(
                    id=int(row['id']),
                    name=row['name'],
                    price=float(row['price']),
                    image=row['image'],
                    release_date=row['release_date'],
                    lte_exists=row['lte_exists'].lower() == 'true',
                )
                phone.save()
        self.stdout.write(
            self.style.SUCCESS('Successfully imported phones')
        )