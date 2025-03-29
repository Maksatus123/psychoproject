from django.contrib import admin
from .models import *

admin.site.register(Answers)
admin.site.register(Questions)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_admin', 'created_by')
    list_filter = ('is_admin',)
    search_fields = ('user__username',)