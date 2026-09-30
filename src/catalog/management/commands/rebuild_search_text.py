from django.core.management.base import BaseCommand

from catalog.models import Product
from catalog.search import refresh_search_index


class Command(BaseCommand):
    help = "Перебудовує нормалізований індекс пошуку товарів."

    def handle(self, *args, **options):
        count = 0
        for product in Product.objects.select_related("brand"):
            refresh_search_index(product)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Оновлено індекс пошуку: {count}"))
