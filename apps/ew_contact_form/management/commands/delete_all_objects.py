from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_models

class Command(BaseCommand):
    help = 'Deletes all objects'

    def handle(self, *args, **options):
        failed_somewhere = False
        max_tries = 100

        while not failed_somewhere and max_tries > 0:
            # some deletions may trigger other deletions and fail; we'll just try many times

            max_tries -= 1

            for model in get_models():
                try:
                    model.objects.all().delete()
                except:
                    failed_somewhere = True

        if max_tries == 0:
            raise Exception("Giving up after 100 tries")
