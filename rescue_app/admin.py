from django.contrib import admin

from .models import (
    Hospital,
    HospitalStaff,
    RescueCenter,
    Ambulance,
    EmergencyReport,
)


# ============================================================
# RESCUE CENTER
# ============================================================

@admin.register(RescueCenter)
class RescueCenterAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'city',
        'phone',
        'capacity',
        'current_cases',
        'is_available',
        'is_active',
    )

    list_filter = (
        'city',
        'state',
        'is_available',
        'is_active',
    )

    search_fields = (
        'name',
        'city',
        'state',
        'phone',
        'email',
    )


# ============================================================
# AMBULANCE
# ============================================================

@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):

    list_display = (
        'ambulance_number',
        'driver_name',
        'driver_phone',
        'rescue_center',
        'status',
        'is_active',
    )

    list_filter = (
        'status',
        'rescue_center',
        'is_active',
    )

    search_fields = (
        'ambulance_number',
        'driver_name',
        'driver_phone',
        'rescue_center__name',
    )


# ============================================================
# HOSPITAL
# ============================================================

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'city',
        'state',
        'phone',
        'has_ambulance',
        'is_available_24_7',
        'is_active',
        'created_at',
    )

    list_filter = (
        'city',
        'state',
        'has_ambulance',
        'is_available_24_7',
        'is_active',
    )

    search_fields = (
        'name',
        'city',
        'state',
        'phone',
        'email',
    )

    readonly_fields = (
        'created_at',
    )


# ============================================================
# HOSPITAL STAFF
# ============================================================

@admin.register(HospitalStaff)
class HospitalStaffAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'hospital',
        'phone',
    )

    list_filter = (
        'hospital',
    )

    search_fields = (
        'user__username',
        'user__email',
        'hospital__name',
        'phone',
    )


# ============================================================
# EMERGENCY REPORT
# ============================================================

@admin.register(EmergencyReport)
class EmergencyReportAdmin(admin.ModelAdmin):

    # --------------------------------------------------------
    # LIST PAGE
    # --------------------------------------------------------

    list_display = (
        'short_report_id',
        'detected_animal',
        'apparent_severity',
        'status',
        'assigned_rescue_center',
        'assigned_ambulance',
        'assigned_hospital',
        'created_at',
    )

    list_filter = (
        'status',
        'apparent_severity',
        'assigned_rescue_center',
        'assigned_hospital',
        'assigned_ambulance',
        'ambulance_assigned',
        'is_animal_detected',
    )

    search_fields = (
        'reporter_name',
        'reporter_phone',
        'reporter_email',
        'detected_animal',
        'detected_injuries',
        'address_text',
        'assigned_rescue_center__name',
        'assigned_hospital__name',
        'assigned_ambulance__ambulance_number',
    )

    # --------------------------------------------------------
    # READ ONLY FIELDS
    # --------------------------------------------------------

    readonly_fields = (
        'report_id',
        'created_at',
        'updated_at',
    )

    # --------------------------------------------------------
    # EMERGENCY REPORT FORM SECTIONS
    # --------------------------------------------------------

    fieldsets = (

        # 1. REPORTER
        (
            'Reporter',
            {
                'fields': (
                    'report_id',
                    'reporter_name',
                    'reporter_phone',
                    'reporter_email',
                )
            }
        ),

        # 2. LOCATION
        (
            'Location',
            {
                'fields': (
                    'latitude',
                    'longitude',
                    'address_text',
                )
            }
        ),

        # 3. ANIMAL & AI ANALYSIS
        (
            'Animal & AI Analysis',
            {
                'fields': (
                    'image',
                    'processed_image',
                    'is_animal_detected',
                    'detected_animal',
                    'detected_injuries',
                    'apparent_severity',
                    'ai_first_aid_guidance',
                )
            }
        ),

        # 4. RESCUE CENTER ASSIGNMENT
        (
            'Rescue Center Assignment',
            {
                'fields': (
                    'assigned_rescue_center',
                )
            }
        ),

        # 5. AMBULANCE ASSIGNMENT
        (
            'Ambulance Assignment',
            {
                'fields': (
                    'assigned_ambulance',
                    'ambulance_assigned',
                )
            }
        ),

        # 6. HOSPITAL ASSIGNMENT
        (
            'Hospital Assignment',
            {
                'fields': (
                    'assigned_hospital',
                )
            }
        ),

        # 7. AMBULANCE TRACKING
        (
            'Ambulance Tracking',
            {
                'fields': (
                    'ambulance_lat',
                    'ambulance_lng',
                    'eta_minutes',
                )
            }
        ),

        # 8. STATUS
        (
            'Status',
            {
                'fields': (
                    'status',
                    'created_at',
                    'updated_at',
                    'notes',
                )
            }
        ),
    )

    # --------------------------------------------------------
    # SHORT REPORT ID
    # --------------------------------------------------------

    @admin.display(description='Report ID')
    def short_report_id(self, obj):
        return str(obj.report_id)[:8]