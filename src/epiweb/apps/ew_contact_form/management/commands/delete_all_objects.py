from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_models

class Command(BaseCommand):
    help = 'Deletes all objects'

    def handle(self, *args, **options):
        for model in get_models():
            model.objects.all().delete()

