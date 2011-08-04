from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_models
from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.core.management.commands.loaddata import Command as LoadDataCommand 
from django.core.management import call_command

@transaction.commit_manually
class Command(BaseCommand):
    help = 'Runs loaddata with pre & post-save signals turned off'

    args = LoadDataCommand.args
    option_list = LoadDataCommand.option_list 

    def handle(self, *args, **options):
        pre_save.receivers = []
        post_save.receivers = []
        call_command('loaddata', *args, **options)

