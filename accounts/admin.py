from django.contrib import admin
from .models import CustomUser, Profile
# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username')
    search_fields = ('email', 'username')
    list_filter = ('is_active', 'is_staff')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
