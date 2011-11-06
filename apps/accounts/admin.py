from django.contrib import admin
from django.contrib.auth.models import User

from .forms import UnicodeUserChangeForm, UnicodeUserCreationForm

current_user_admin = type(admin.site._registry[User])
class UnicodeUserAdmin(current_user_admin):
    form = UnicodeUserChangeForm
    add_form = UnicodeUserCreationForm

admin.site.unregister(User)
admin.site.register(User, UnicodeUserAdmin)


