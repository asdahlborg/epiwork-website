from django.conf import settings as django_settings


"""
    Disables the latest news plugin
    Defaults to false
"""
DISABLE_LATEST_ENTRIES_PLUGIN = getattr(django_settings, 'JOURNAL_DISABLE_LATEST_ENTRIES_PLUGIN', False)
