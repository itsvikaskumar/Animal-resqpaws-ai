import uuid
from django.db import models
from django.contrib.auth.models import User
from hospitals.models import Hospital, Ambulance

class RescueReport(models.Model):
    SPECIES_CHOICES = (
        ('DOG', 'Dog / Puppy'),
        ('CAT', 'Cat / Kitten'),
        ('BIRD', 'Bird / Avian'),
        ('COW', 'Cow / Cattle'),
        ('HORSE', 'Horse / Donkey'),
        ('WILDLIFE', 'Wildlife / Exotic'),
        ('OTHER', 'Other Animal'),
    )

    SEVERITY_CHOICES = (
        ('CRITICAL', 'Critical (Immediate Life Threat)'),
        ('SEVERE', 'Severe (Urgent Care Needed)'),
        ('MODERATE', 'Moderate (Stable / Fractures / Wounds)'),
        ('MINOR', 'Minor (Superficial / Checkup)'),
    )

    STATUS_CHOICES = (
        ('REPORTED', 'Reported & Analyzed by AI'),
        ('ASSIGNED', 'Hospital Assigned & Reviewing'),
        ('DISPATCHED', 'Ambulance Dispatched / En Route'),
        ('ON_SCENE', 'Rescue Team Arrived On Scene'),
        ('RESCUED', 'Animal Secured & In Transit'),
        ('IN_TREATMENT', 'Admitted to Hospital & Under Treatment'),
        ('RECOVERED', 'Recovered / Safe / Adoptable'),
        ('CLOSED', 'Case Resolved & Closed'),
    )

    tracking_id = models.CharField(max_length=20, unique=True, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reports')
    reporter_name = models.CharField(max_length=120, default='Anonymous Citizen')
    reporter_phone = models.CharField(max_length=25, blank=True, null=True)

    image = models.ImageField(upload_to='rescues/%Y/%m/')
    annotated_image = models.CharField(max_length=255, blank=True, null=True)
    
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES, default='DOG')
    species_detected_by_ai = models.CharField(max_length=100, blank=True, null=True)
    injury_severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MODERATE')
    ai_confidence = models.FloatField(default=90.0)
    ai_symptoms = models.TextField(blank=True, null=True)

    latitude = models.FloatField(help_text="GPS Latitude")
    longitude = models.FloatField(help_text="GPS Longitude")
    location_address = models.CharField(max_length=255, blank=True, null=True)
    landmark_notes = models.TextField(blank=True, null=True, help_text="e.g. Near Blue Gate, behind supermarket")

    hospital_assigned = models.ForeignKey(Hospital, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_reports')
    ambulance_assigned = models.ForeignKey(Ambulance, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_reports')
    
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='REPORTED')
    first_aid_viewed = models.BooleanField(default=False)
    medical_notes = models.TextField(blank=True, null=True)
    recovery_photo = models.ImageField(upload_to='recovery/%Y/%m/', blank=True, null=True)

    reported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            short_id = uuid.uuid4().hex[:6].upper()
            self.tracking_id = f"RQ-{short_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_id} - {self.get_species_display()} ({self.get_injury_severity_display()}) - {self.get_status_display()}"

    @property
    def severity_badge_class(self):
        mapping = {
            'CRITICAL': 'bg-danger text-white',
            'SEVERE': 'bg-warning text-dark',
            'MODERATE': 'bg-primary text-white',
            'MINOR': 'bg-success text-white'
        }
        return mapping.get(self.injury_severity, 'bg-secondary text-white')

    @property
    def status_badge_class(self):
        mapping = {
            'REPORTED': 'bg-secondary text-white',
            'ASSIGNED': 'bg-info text-dark',
            'DISPATCHED': 'bg-warning text-dark',
            'ON_SCENE': 'bg-primary text-white',
            'RESCUED': 'bg-dark text-white',
            'IN_TREATMENT': 'bg-indigo text-white',
            'RECOVERED': 'bg-success text-white',
            'CLOSED': 'bg-secondary text-white',
        }
        return mapping.get(self.status, 'bg-secondary text-white')


class RescueStatusLog(models.Model):
    report = models.ForeignKey(RescueReport, on_delete=models.CASCADE, related_name='status_logs')
    status = models.CharField(max_length=25)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.report.tracking_id}: {self.status} at {self.timestamp.strftime('%H:%M:%S')}"
