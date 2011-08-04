from django.contrib import admin

from apps.survey.models import SurveyUser, Profile, Participation

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated', 'valid', 'created')
    ordering = ('user__name',)
    search_fields = ('user__name',)
    list_filter = ('valid',)

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'epidb_id')
    ordering = ('-date',)

class SurveyUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_participation_date', 'global_id')
    ordering = ('name',)
    search_fields = ('name',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(SurveyUser, SurveyUserAdmin)

