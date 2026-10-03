from django.contrib import admin
from .models import Hospital, Ambulance

class AmbulanceInline(admin.TabularInline):
    model = Ambulance
    extra = 1

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone', 'capacity', 'current_occupancy', 'has_24_7_ambulance', 'is_active')
    list_filter = ('city', 'has_24_7_ambulance', 'is_active')
    search_fields = ('name', 'city', 'address', 'phone')
    inlines = [AmbulanceInline]

@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    list_display = ('vehicle_number', 'hospital', 'driver_name', 'driver_phone', 'status', 'last_updated')
    list_filter = ('status', 'hospital')
    search_fields = ('vehicle_number', 'driver_name', 'driver_phone')
