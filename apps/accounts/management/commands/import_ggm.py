import MySQLdb

from django.core.management.base import NoArgsCommand, BaseCommand 
from django.db import transaction
from django.contrib.auth.models import User

from apps.reminder.models import UserReminderInfo
from apps.survey.models import SurveyUser

class Command(NoArgsCommand):

    @transaction.commit_on_success
    def handle_noargs(self, **options):
        c = MySQLdb.connect(host="localhost", user="root", passwd="", db="ggm_existing_tmp", charset='utf8')
        cursor = c.cursor ()
        cursor.execute ("SELECT * FROM `meter`")

        rows = cursor.fetchall()
        for i, row in enumerate(rows):
            meter_id, UUID, email, naam, postcode, geb_datum, geslacht, password, _pw_new, laatste_meting, laatste_mail, herinnering, reken_postcode, wil_herinnering, stress = row
            print i, email
            if i > 10:
                break

            if User.objects.filter(email=email).count():
                continue

            u = User(
                email=email,
                username=email,
            )
            u.set_password(password)
            u.save()

            reminder = UserReminderInfo.objects.create(
                user=u,
                active=(wil_herinnering == 1),
                language='nl',
            )

            survey_user = SurveyUser.objects.create(
                user=u,
                global_id=UUID,
                name=naam,
                last_participation_date=laatste_meting,
            )

            naam # may be put in the SurveyUser
            
            # postcode: somewhere in 'intake'?
            # reken_postcode: same same
            # geb_datum, geslacht: same same
            # laatste_mail is unusable

        cursor.close ()
        c.close ()

