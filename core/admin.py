from django.contrib import admin
from .models import ContactMessage, EmergencyHotline

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')

@admin.register(EmergencyHotline)
class EmergencyHotlineAdmin(admin.ModelAdmin):
    list_display = ('region_name', 'phone_number', 'service_type', 'is_active')
    list_filter = ('is_active',)
