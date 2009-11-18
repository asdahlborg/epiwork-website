from django.dispatch import dispatcher
from django.db.models import signals

from epiweb.apps.survey import models

def post_syncdb(sender, **kwargs):
    app = kwargs['app']
    created_models = kwargs['created_models']
    if (app == models) and (models.Survey in created_models):
        definition = ''
        import hashlib
        hash = hashlib.sha1(definition)
        hash.digest()

        survey = models.Survey()
        survey.title = 'Dummy Survey'
        survey.definition = definition
        survey.hash = hash.hexdigest()
        survey.active = True
        survey.save()

signals.post_syncdb.connect(post_syncdb)

