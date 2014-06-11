from django.contrib import admin
from models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_filter = ('free_game', )


admin.site.register(Profile, ProfileAdmin)