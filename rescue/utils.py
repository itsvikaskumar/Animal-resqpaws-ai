import math
from django.core.mail import send_mail
from django.conf import settings
from hospitals.models import Hospital

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on the earth in kilometers (Haversine formula).
    """
    R = 6371.0 # Earth radius in kilometers

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def find_nearest_hospital(latitude, longitude):
    """
    Finds the nearest active animal hospital/rescue center based on GPS coordinates.
    Returns (nearest_hospital, distance_km).
    """
    hospitals = Hospital.objects.filter(is_active=True)
    if not hospitals.exists():
        return None, 0.0

    nearest = None
    min_dist = float('inf')

    for hospital in hospitals:
        dist = haversine_distance(latitude, longitude, hospital.latitude, hospital.longitude)
        if dist < min_dist:
            min_dist = dist
            nearest = hospital

    return nearest, min_dist


def send_emergency_alert(rescue_report):
    """
    Triggers emergency alert email and notification logs to the assigned hospital.
    """
    if not rescue_report.hospital_assigned:
        return

    hospital = rescue_report.hospital_assigned
    subject = f"🚨 URGENT ANIMAL EMERGENCY: {rescue_report.get_injury_severity_display()} ({rescue_report.tracking_id})"
    
    message = (
        f"EMERGENCY DISPATCH ALERT\n"
        f"----------------------------------------\n"
        f"Case Tracking ID: {rescue_report.tracking_id}\n"
        f"Species: {rescue_report.get_species_display()}\n"
        f"AI Severity Level: {rescue_report.injury_severity} (Confidence: {rescue_report.ai_confidence}%)\n"
        f"GPS Location: {rescue_report.latitude}, {rescue_report.longitude}\n"
        f"Address / Landmark: {rescue_report.location_address or 'Not specified'} | {rescue_report.landmark_notes or ''}\n"
        f"Reporter: {rescue_report.reporter_name} (Phone: {rescue_report.reporter_phone or 'N/A'})\n\n"
        f"Please log in to your ResQPaws Hospital Dashboard to review images, triage the animal, and dispatch an ambulance.\n"
    )

    recipient_list = []
    if hospital.email:
        recipient_list.append(hospital.email)

    try:
        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=True
            )
    except Exception as e:
        print(f"Error sending emergency email alert: {e}")
