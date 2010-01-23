from django.contrib import admin

from epiweb.apps.survey.models import Profile, Participation

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated', 'valid', 'created')
    ordering = ('user__username',)
    search_fields = ('user__username',)

class ParticipationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Participation, ParticipationAdmin)

