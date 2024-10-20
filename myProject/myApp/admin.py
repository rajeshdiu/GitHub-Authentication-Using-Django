from django.contrib import admin
from myApp.models import *


@admin.register(Custom_User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type','is_verified','first_name', 'last_name')
    search_fields = ('username', 'email')
    list_filter = ('user_type',)