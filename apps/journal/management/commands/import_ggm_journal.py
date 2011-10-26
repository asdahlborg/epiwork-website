import MySQLdb

from django.core.management.base import NoArgsCommand, BaseCommand 
from django.db import transaction
from django.template.defaultfilters import slugify

from apps.journal.models import Entry

class Command(NoArgsCommand):

    @transaction.commit_on_success
    def handle_noargs(self, **options):
        c = MySQLdb.connect(host="localhost", user="root", passwd="", db="tmp_ggm_news", charset='utf8')
        cursor = c.cursor ()
        cursor.execute ("SELECT * FROM `articles_filed`")

        rows = cursor.fetchall()
        for i, row in enumerate(rows):
            id, art_id, date, section_name, title, html, abstract = row

            entry = Entry.objects.language('nl').create(
                slug=slugify(title)[:50],
                image=None,
                alignment=None,
                is_published=True,
                pub_date=date,
                created=date,
                updated=date,
                category=None,

                title=title,
                excerpt=abstract,
                content=html,
            )

            
            # Next: translate
            #translations = TranslatedFields(
                #title           = models.CharField(_('Title'), max_length=255),
                #excerpt         = models.TextField(_('Excerpt'), blank=True),
                #content         = models.TextField(_('Content'), blank=True),
            #)

        cursor.close ()
        c.close ()

