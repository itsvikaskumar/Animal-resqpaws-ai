from django.contrib import admin
from .models import RescueReport, RescueStatusLog

class RescueStatusLogInline(admin.TabularInline):
    model = RescueStatusLog
    extra = 1

@admin.register(RescueReport)
class RescueReportAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'species', 'injury_severity', 'status', 'hospital_assigned', 'ambulance_assigned', 'reported_at')
    list_filter = ('injury_severity', 'status', 'species', 'reported_at')
    search_fields = ('tracking_id', 'reporter_name', 'reporter_phone', 'location_address')
    inlines = [RescueStatusLogInline]

@admin.register(RescueStatusLog)
class RescueStatusLogAdmin(admin.ModelAdmin):
    list_display = ('report', 'status', 'timestamp', 'updated_by')
    list_filter = ('status', 'timestamp')
