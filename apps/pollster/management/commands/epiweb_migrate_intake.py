from optparse import make_option
from django.core.management.base import CommandError, BaseCommand
import cPickle as pickle
import MySQLdb

def yearmonth(date):
    if not date:
        return ''
    return "%d/%02d" % (date.year, date.month)

def setmulti(intake, dest, data, src, index):
    if src not in data:
        return
    val = int(data[src][index-1])
    if val != 99:
        setattr(intake, "%s_%d" % (dest, index), True)
        setattr(intake, "%s_%d_open" % (dest, index), val)

class Command(BaseCommand):
    help = 'Register a question data type.'
    option_list = BaseCommand.option_list + (
        make_option(None, '--host', action='store', type="string",
                    dest='host',
                    help='Source database host'),
        make_option('-p', '--password', action='store', type="string",
                    dest='password',
                    help='Source database password'),
        make_option('-d', '--database', action='store', type="string",
                    dest='database',
                    help='Source database name'),
        make_option('-u', '--username', action='store', type="string",
                    dest='username',
                    help='User name to connect to the source database'),
    )

    def convert(self, data, intake):
        intake.Q1 = data["IntakeQ1"]
        intake.Q2 = yearmonth(data["IntakeQ2"])
        intake.Q3 = data["IntakeQ3"]
        if data["IntakeQ4"]:
            intake.Q4b = 0
            intake.Q4b_0_open = data["IntakeQ4"]
        if data.get("IntakeQ5"):
            intake.Q5_1 = 1 in data["IntakeQ5"]
            intake.Q5_2 = 2 in data["IntakeQ5"]
            intake.Q5_3 = 3 in data["IntakeQ5"]
        setmulti(intake, "Q6", data, "IntakeQ6", 1)
        setmulti(intake, "Q6", data, "IntakeQ6", 2)
        setmulti(intake, "Q6", data, "IntakeQ6", 3)
        setmulti(intake, "Q6", data, "IntakeQ6", 4)
        setmulti(intake, "Q6", data, "IntakeQ6", 5)
        intake.Q6b = data.get("IntakeQ6b")
        if data.get("IntakeQ7"):
            intake.Q7_0 = data["IntakeQ7"] == 0
            intake.Q7_1 = data["IntakeQ7"] == 1
            intake.Q7_2 = data["IntakeQ7"] == 2
            intake.Q7_3 = data["IntakeQ7"] == 3
            intake.Q7_4 = data["IntakeQ7"] == 4
            intake.Q7_5 = data["IntakeQ7"] == 5
        intake.Q7b = data["IntakeQ7b"]
        if intake.Q7b == 4:
            intake.Q7b = 3
        if intake.Q7b == 5:
            intake.Q7b = 4
        intake.Q9 = data["IntakeQ8"]
        intake.Q10 = data["IntakeQ10"]
        q10b = data.get("IntakeQ10b")
        if q10b:
            intake.Q10b = '1'
            intake.Q10b_1_open = q10b
        else:
            intake.Q10b = '0'
        if data.get("IntakeQ10c"):
            intake.Q10c_0 = 0 in data["IntakeQ10c"]
            intake.Q10c_1 = 1 in data["IntakeQ10c"]
            intake.Q10c_2 = 2 in data["IntakeQ10c"]
            intake.Q10c_3 = 3 in data["IntakeQ10c"]
            intake.Q10c_4 = 4 in data["IntakeQ10c"]
            intake.Q10c_5 = 5 in data["IntakeQ10c"]
            intake.Q10c_6 = 6 in data["IntakeQ10c"]
            intake.Q10c_7 = 7 in data["IntakeQ10c"]
            intake.Q10c_8 = 8 in data["IntakeQ10c"]
            intake.Q10c_9 = 9 in data["IntakeQ10c"]
        if data.get("IntakeQ12"):
            intake.Q11_1 = 0 in data["IntakeQ12"]
            intake.Q11_2 = 1 in data["IntakeQ12"]
            intake.Q11_3 = 2 in data["IntakeQ12"]
            intake.Q11_4 = 3 in data["IntakeQ12"]
            intake.Q11_5 = 4 in data["IntakeQ12"]
            intake.Q11_6 = 5 in data["IntakeQ12"]
        intake.Q12 = data["IntakeQ13"]
        intake.Q12b = data["IntakeQ13b"]
        q14 = data.get("IntakeQ14")
        if q14 == 0:
            intake.Q13 = 0
        elif q14 == 1:
            intake.Q13 = 2
        elif q14 == 2:
            intake.Q13 = 3
        elif q14 == 3:
            intake.Q13 = 4
        if data.get("IntakeQ15"):
            intake.Q14_0 = 0 in data["IntakeQ15"]
            intake.Q14_1 = 1 in data["IntakeQ15"]
            intake.Q14_2 = 2 in data["IntakeQ15"]
            intake.Q14_3 = 3 in data["IntakeQ15"]
        intake.Q8 = data["IntakeQ18"]
        intake.Q15_0 = data["IntakeQ16"] == 0
        intake.Q15_1 = data["IntakeQ16"] == 1
        intake.Q15_2 = data["IntakeQ16"] == 2
        intake.Q15_3 = data["IntakeQ16"] == 3
        intake.Q15_4 = data["IntakeQ16"] == 4
        if data.get("IntakeQ17"):
            intake.Q16_0 = 0 in data["IntakeQ17"]
            intake.Q16_1 = 1 in data["IntakeQ17"]
            intake.Q16_2 = 2 in data["IntakeQ17"]
            intake.Q16_3 = 3 in data["IntakeQ17"]
            intake.Q16_4 = 4 in data["IntakeQ17"]

    def load_profiles(self, options):
        verbosity = options.get('verbosity')
        database = options.get('database')
        host = options.get('host') or ''
        username = options.get('username')
        password = options.get('password') or ''
        db = MySQLdb.connect(user=username, passwd=password, host=host, db=database)
        cursor = db.cursor()

        surveyusers = {}
        cursor.execute("""
        SELECT SU.id, SUU.user_id, SU.global_id, SU.deleted, SU.last_participation_id, SU.last_participation_date, SU.name
          FROM survey_surveyuser SU, survey_surveyuser_user SUU
         WHERE SUU.surveyuser_id = SU.id""")
        for surveyuser in cursor.fetchall():
            this = {
                "id": surveyuser[0],
                "user_id": surveyuser[1],
                "global_id": surveyuser[2],
                "deleted": surveyuser[3],
                "last_participation_id": surveyuser[4],
                "last_participation_date": surveyuser[5],
                "name": surveyuser[6]
            }
            surveyusers[this["id"]] = this

        profiles = []
        cursor.execute("""
        SELECT user_id, updated, survey_id, data
          FROM survey_profile""")
        for profile in cursor.fetchall():
            this = {
                "user_id": profile[0],
                "updated": profile[1],
                "survey_id": profile[2],
                "data": profile[3]
            }
            if this["data"]:
                this["data"] = pickle.loads(this["data"])
            this["user"] = surveyusers.get(this["user_id"])
            if verbosity > 0 and not this["user"]:
                self.stderr.write("missing user %s\n" % (this["user_id"], ))
            profiles.append(this)
        return profiles

    def handle(self, *args, **options):
        from apps.pollster import models

        verbosity = int(options.get('verbosity'))

        if 'database' not in options:
            raise CommandError("you need to specify the source database")

        Intake = models.Survey.get_by_shortname('intake').as_model()
        profiles = self.load_profiles(options)
        count = 0
        for p in self.load_profiles(options):
            count += 1
            if verbosity > 1:
                self.stdout.write("importing %s of %s\n" % (count, len(profiles)))
            u = p["user"]
            if u and verbosity > 2:
                self.stdout.write("%s (user %s, global_id %s)\n" % (u["name"], u["user_id"], u["global_id"]))
            if p["updated"]:
                data = p["data"]
                if verbosity > 2:
                    self.stdout.write("  compiled on %s: %s\n" % (p["updated"], data))
                intake = Intake()
                intake.user = u["user_id"]
                intake.global_id = u["global_id"]
                intake.timestamp = p["updated"]
                intake.channel = 'migrate-intake'
                self.convert(data, intake)
                intake.save()
