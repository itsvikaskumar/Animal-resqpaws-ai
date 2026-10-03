from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('CITIZEN', 'Citizen / Good Samaritan'),
        ('HOSPITAL_STAFF', 'Hospital / Rescue Staff'),
        ('ADMIN', 'System Administrator'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CITIZEN')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    affiliated_hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='staff_members'
    )
    is_verified_rescuer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_hospital_staff(self):
        return self.role in ['HOSPITAL_STAFF', 'ADMIN'] or self.user.is_superuser

    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.user.is_superuser


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
