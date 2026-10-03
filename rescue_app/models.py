import uuid
from django.db import models
from django.contrib.auth.models import User


class RescueCenter(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100, default='Dehradun')
    state = models.CharField(max_length=100, default='Uttarakhand')
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    latitude = models.FloatField()
    longitude = models.FloatField()

    capacity = models.PositiveIntegerField(default=10)
    current_cases = models.PositiveIntegerField(default=0)

    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.city})"


class Ambulance(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('ASSIGNED', 'Assigned'),
        ('EN_ROUTE', 'En Route'),
        ('BUSY', 'Busy'),
        ('MAINTENANCE', 'Maintenance'),
        ('OFFLINE', 'Offline'),
    ]

    ambulance_number = models.CharField(
        max_length=50,
        unique=True
    )

    rescue_center = models.ForeignKey(
        RescueCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ambulances'
    )

    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AVAILABLE'
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ambulance_number} - {self.driver_name}"


class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100, default='Dehradun')
    state = models.CharField(max_length=100, default='Uttarakhand')

    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField()

    latitude = models.FloatField()
    longitude = models.FloatField()

    has_ambulance = models.BooleanField(default=True)
    is_available_24_7 = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.city})"


class HospitalStaff(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='hospital_profile'
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='staff'
    )

    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.hospital.name}"


class EmergencyReport(models.Model):

    STATUS_CHOICES = [
        ('REPORTED', 'Reported / Triage Pending'),
        ('SEARCHING', 'Searching Nearby Rescue Centers'),
        ('DISPATCHED', 'Rescue Team Dispatched / Ambulance En Route'),
        ('ADMITTED', 'Arrived at Hospital / Under Treatment'),
        ('RESOLVED', 'Rescued & Recovered'),
        ('CANCELLED', 'Cancelled'),
    ]

    SEVERITY_CHOICES = [
        ('NORMAL', 'Minor / Normal (Non-Emergency)'),
        ('MODERATE', 'Moderate Injury'),
        ('CRITICAL', 'Critical / Severe (Immediate Rescue Needed)'),
        ('UNKNOWN', 'Unverified / Direct Report'),
    ]

    report_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    # Reporter Information
    reporter_name = models.CharField(max_length=150)
    reporter_phone = models.CharField(max_length=20)
    reporter_email = models.EmailField()

    # Location
    latitude = models.FloatField()
    longitude = models.FloatField()

    address_text = models.TextField(
        blank=True,
        help_text="Landmark or street description"
    )

    # Image & AI
    image = models.ImageField(
        upload_to='reports/',
        blank=True,
        null=True
    )

    processed_image = models.ImageField(
        upload_to='reports/processed/',
        blank=True,
        null=True
    )

    is_animal_detected = models.BooleanField(default=False)

    detected_animal = models.CharField(
        max_length=100,
        default='Unknown'
    )

    detected_injuries = models.TextField(
        blank=True,
        default='None detected'
    )

    apparent_severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='UNKNOWN'
    )

    ai_first_aid_guidance = models.TextField(
        blank=True
    )

    # Rescue Center Assignment
    assigned_rescue_center = models.ForeignKey(
        RescueCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_reports'
    )

    # Hospital Assignment
    assigned_hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_cases'
    )

    # Ambulance Assignment
    assigned_ambulance = models.ForeignKey(
        Ambulance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_reports'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REPORTED'
    )

    # Ambulance Tracking
    ambulance_assigned = models.BooleanField(default=False)

    ambulance_lat = models.FloatField(
        null=True,
        blank=True
    )

    ambulance_lng = models.FloatField(
        null=True,
        blank=True
    )

    eta_minutes = models.IntegerField(default=15)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Case #{str(self.report_id)[:8]} - "
            f"{self.detected_animal} "
            f"({self.apparent_severity})"
        )