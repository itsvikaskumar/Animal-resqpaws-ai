from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, default='City Center')
    phone = models.CharField(max_length=25)
    emergency_phone = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    latitude = models.FloatField(help_text="Hospital GPS Latitude (e.g. 28.6139)")
    longitude = models.FloatField(help_text="Hospital GPS Longitude (e.g. 77.2090)")
    capacity = models.PositiveIntegerField(default=25, help_text="Total animal ward capacity")
    current_occupancy = models.PositiveIntegerField(default=0)
    has_24_7_ambulance = models.BooleanField(default=True)
    has_icu = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.city})"

    @property
    def available_beds(self):
        return max(0, self.capacity - self.current_occupancy)

    @property
    def available_ambulances_count(self):
        return self.ambulances.filter(status='AVAILABLE').count()


class Ambulance(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Available at Base'),
        ('DISPATCHED', 'Dispatched / En Route'),
        ('ON_SCENE', 'On Scene / Rescuing'),
        ('RETURNING', 'Transporting to Clinic'),
        ('MAINTENANCE', 'Under Maintenance / Off Duty'),
    )

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='ambulances')
    vehicle_number = models.CharField(max_length=50)
    driver_name = models.CharField(max_length=120)
    driver_phone = models.CharField(max_length=25)
    paramedic_name = models.CharField(max_length=120, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    current_latitude = models.FloatField(blank=True, null=True)
    current_longitude = models.FloatField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ambulance {self.vehicle_number} - {self.hospital.name} ({self.get_status_display()})"
