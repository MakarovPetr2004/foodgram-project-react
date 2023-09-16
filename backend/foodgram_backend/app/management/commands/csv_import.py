import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from app.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        CSV_DIR = Path('static', 'data')
        model = Ingredient
        with open(Path(CSV_DIR, 'ingredients.csv'), mode='r',
                  encoding='utf8') as f:
            reader = csv.DictReader(f)
            counter = 0
            objects_to_create = []
            for row in reader:
                counter += 1
                args = dict(**row)
                objects_to_create.append(model(**args))
            model.objects.bulk_create(objects_to_create,
                                      ignore_conflicts=True)
        self.stdout.write("Все данные загружены!")
