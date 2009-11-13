from django.dispatch import Signal

survey_done = Signal(providing_args=["user", "answers", "request"])

