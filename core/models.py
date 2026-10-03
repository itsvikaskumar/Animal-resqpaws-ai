from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ['-created_at']


class EmergencyHotline(models.Model):
    region_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30)
    service_type = models.CharField(max_length=100, default='24/7 Animal Ambulance & Rescue')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.region_name} - {self.phone_number}"
