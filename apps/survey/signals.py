import django.dispatch

response_submit = django.dispatch.Signal(
                        providing_args=['user', 'date', 'user_id',
                                        'survey_id', 'answers'])

profile_update = django.dispatch.Signal(
                        providing_args=['user', 'date', 'user_id',
                                        'survey_id', 'answers'])

