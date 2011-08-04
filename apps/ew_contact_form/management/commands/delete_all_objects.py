from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_models
from django.db import transaction

@transaction.commit_manually
class Command(BaseCommand):
    help = 'Deletes all objects'

    def handle(self, *args, **options):
        failed_somewhere = True
        max_tries = 100

        while failed_somewhere and max_tries > 0:
            # some deletions may trigger other deletions and fail; we'll just try many times
            failed_somewhere = False

            max_tries -= 1

            for model in get_models():
                try:
                    model.objects.all().delete()
                except Exception, e:
                    print e
                    failed_somewhere = True

        transaction.commit()
        if max_tries == 0:
            raise Exception("Giving up after 100 tries")

