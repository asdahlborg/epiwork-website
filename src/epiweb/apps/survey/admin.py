from django.contrib import admin

from epiweb.apps.survey.models import SurveyUser, Profile, Participation

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated', 'valid', 'created')
    ordering = ('user__username',)
    search_fields = ('user__username',)
    list_filter = ('valid',)

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'date')
    ordering = ('-date',)

class SurveyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_participation_date', 'global_id')
    ordering = ('user__username',)
    search_fields = ('user__username',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(SurveyUser, SurveyUserAdmin)

