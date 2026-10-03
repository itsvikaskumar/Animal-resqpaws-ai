from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'affiliated_hospital', 'is_verified_rescuer', 'created_at')
    list_filter = ('role', 'is_verified_rescuer', 'affiliated_hospital')
    search_fields = ('user__username', 'user__email', 'phone', 'address')
