"""
ResQPaws AI - Seed Data Initializer
Populates database with sample hospitals, ambulances, test users, and emergency logs.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resqpaws_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from hospitals.models import Hospital, Ambulance
from core.models import EmergencyHotline
from rescue.models import RescueReport, RescueStatusLog

def seed_database():
    print("🌱 Seeding ResQPaws AI Database...")

    # 1. Create Admin User
    admin_user, created = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@resqpaws.ai',
        'first_name': 'System',
        'last_name': 'Administrator',
        'is_staff': True,
        'is_superuser': True
    })
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        admin_profile.role = 'ADMIN'
        admin_profile.phone = '+1 (800) 555-0100'
        admin_profile.save()
        print("✅ Superuser created: admin / admin123")

    # 2. Create Hospitals & Clinics
    hospitals_data = [
        {
            'name': 'City Central Veterinary Trauma Center',
            'address': 'Plot 14, Main Avenue, Health District',
            'city': 'Metropolis Central',
            'phone': '+1 (555) 901-2233',
            'emergency_phone': '+1 (800) 737-7729',
            'email': 'central.trauma@resqpaws.ai',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'capacity': 35,
            'current_occupancy': 12,
            'has_24_7_ambulance': True,
            'has_icu': True,
        },
        {
            'name': 'Paws & Wings Emergency Sanctuary',
            'address': '88 Green Park Boulevard, North Sector',
            'city': 'Metropolis North',
            'phone': '+1 (555) 882-3344',
            'emergency_phone': '+1 (800) 737-7730',
            'email': 'north.sanctuary@resqpaws.ai',
            'latitude': 28.6448,
            'longitude': 77.2167,
            'capacity': 25,
            'current_occupancy': 8,
            'has_24_7_ambulance': True,
            'has_icu': True,
        },
        {
            'name': 'Hope Animal Rescue & Critical Care Hospital',
            'address': '204 South Ring Road, East Sector',
            'city': 'Metropolis East',
            'phone': '+1 (555) 773-4455',
            'emergency_phone': '+1 (800) 737-7731',
            'email': 'hope.rescue@resqpaws.ai',
            'latitude': 28.5800,
            'longitude': 77.2300,
            'capacity': 20,
            'current_occupancy': 5,
            'has_24_7_ambulance': True,
            'has_icu': False,
        },
        {
            'name': 'Blue Cross Mobile Veterinary Unit',
            'address': 'West Ring Highway, Sector 18',
            'city': 'Metropolis West',
            'phone': '+1 (555) 664-5566',
            'emergency_phone': '+1 (800) 737-7732',
            'email': 'bluecross.west@resqpaws.ai',
            'latitude': 28.6250,
            'longitude': 77.1800,
            'capacity': 15,
            'current_occupancy': 4,
            'has_24_7_ambulance': True,
            'has_icu': True,
        }
    ]

    hospitals_objs = []
    for h_data in hospitals_data:
        hosp, _ = Hospital.objects.get_or_create(name=h_data['name'], defaults=h_data)
        hospitals_objs.append(hosp)
    print(f"✅ Created/Verified {len(hospitals_objs)} Animal Hospitals.")

    # 3. Create Hospital Staff User
    vet_user, created = User.objects.get_or_create(username='vet_staff', defaults={
        'email': 'vet.doctor@resqpaws.ai',
        'first_name': 'Dr. Sarah',
        'last_name': 'Jenkins',
    })
    if created:
        vet_user.set_password('staff123')
        vet_user.save()
        vet_profile, _ = UserProfile.objects.get_or_create(user=vet_user)
        vet_profile.role = 'HOSPITAL_STAFF'
        vet_profile.affiliated_hospital = hospitals_objs[0]
        vet_profile.phone = '+1 (555) 332-1100'
        vet_profile.save()
        print("✅ Hospital staff created: vet_staff / staff123")

    # 4. Create Citizen User
    citizen_user, created = User.objects.get_or_create(username='citizen1', defaults={
        'email': 'citizen@example.com',
        'first_name': 'Alex',
        'last_name': 'Rivera',
    })
    if created:
        citizen_user.set_password('user123')
        citizen_user.save()
        c_profile, _ = UserProfile.objects.get_or_create(user=citizen_user)
        c_profile.role = 'CITIZEN'
        c_profile.phone = '+1 (555) 441-9988'
        c_profile.save()
        print("✅ Citizen user created: citizen1 / user123")

    # 5. Populate Ambulance Fleets
    ambulances_data = [
        {'hospital': hospitals_objs[0], 'vehicle_number': 'AMB-METRO-01', 'driver_name': 'Robert Taylor', 'driver_phone': '+1 (555) 234-5678', 'paramedic_name': 'Nurse Emily', 'status': 'AVAILABLE', 'current_latitude': 28.6139, 'current_longitude': 77.2090},
        {'hospital': hospitals_objs[0], 'vehicle_number': 'AMB-METRO-02', 'driver_name': 'Marcus Vance', 'driver_phone': '+1 (555) 345-6789', 'paramedic_name': 'EMT David', 'status': 'AVAILABLE', 'current_latitude': 28.6145, 'current_longitude': 77.2100},
        {'hospital': hospitals_objs[1], 'vehicle_number': 'AMB-NORTH-01', 'driver_name': 'James Miller', 'driver_phone': '+1 (555) 456-7890', 'paramedic_name': 'Nurse Chloe', 'status': 'AVAILABLE', 'current_latitude': 28.6448, 'current_longitude': 77.2167},
        {'hospital': hospitals_objs[2], 'vehicle_number': 'AMB-EAST-01', 'driver_name': 'Liam Wilson', 'driver_phone': '+1 (555) 567-8901', 'paramedic_name': 'EMT Lucas', 'status': 'AVAILABLE', 'current_latitude': 28.5800, 'current_longitude': 77.2300},
    ]

    for amb_data in ambulances_data:
        Ambulance.objects.get_or_create(vehicle_number=amb_data['vehicle_number'], defaults=amb_data)
    print("✅ Ambulance fleets initialized.")

    # 6. Emergency Hotlines
    EmergencyHotline.objects.get_or_create(region_name='Metro Central 24/7 Dispatch', defaults={'phone_number': '1800-737-7729', 'service_type': 'Trauma Ambulance & Emergency Surgery'})
    EmergencyHotline.objects.get_or_create(region_name='Wildlife & Avian Rapid Rescue', defaults={'phone_number': '1800-945-3227', 'service_type': 'Exotic Animal / Bird Sanctuary'})
    print("✅ Emergency hotlines added.")

    # 7. Sample Initial Emergency Reports
    if RescueReport.objects.count() == 0:
        rep1 = RescueReport.objects.create(
            tracking_id="RQ-7A8B1C",
            reporter=citizen_user,
            reporter_name="Alex Rivera",
            reporter_phone="+1 (555) 441-9988",
            species="DOG",
            species_detected_by_ai="Canine (Stray Dog)",
            injury_severity="CRITICAL",
            ai_confidence=96.4,
            ai_symptoms="Extensive Active Hemorrhage | Right Hind Leg Deformity",
            latitude=28.6180,
            longitude=77.2120,
            location_address="Near Connaught Place Outer Circle, Gate 4",
            landmark_notes="Lying quietly next to the newsstand under a tree",
            hospital_assigned=hospitals_objs[0],
            status="DISPATCHED",
            first_aid_viewed=True,
        )
        amb1 = Ambulance.objects.filter(hospital=hospitals_objs[0]).first()
        if amb1:
            amb1.status = 'DISPATCHED'
            amb1.save()
            rep1.ambulance_assigned = amb1
            rep1.save()

        RescueStatusLog.objects.create(
            report=rep1,
            status="REPORTED",
            message="Citizen uploaded image. AI classified Critical Canine Trauma with 96.4% confidence."
        )
        RescueStatusLog.objects.create(
            report=rep1,
            status="ASSIGNED",
            message=f"Dispatched nearest triage center: {hospitals_objs[0].name} (0.8 km away)."
        )
        RescueStatusLog.objects.create(
            report=rep1,
            status="DISPATCHED",
            message=f"Ambulance {amb1.vehicle_number if amb1 else 'AMB-01'} dispatched. Paramedic En Route (ETA 8 mins)."
        )

        # Report 2 (Cat)
        rep2 = RescueReport.objects.create(
            tracking_id="RQ-3D9E2F",
            reporter=citizen_user,
            reporter_name="Alex Rivera",
            reporter_phone="+1 (555) 441-9988",
            species="CAT",
            species_detected_by_ai="Feline (Kitten)",
            injury_severity="MODERATE",
            ai_confidence=91.2,
            ai_symptoms="Superficial Leg Abrasion | Dehydration",
            latitude=28.6410,
            longitude=77.2150,
            location_address="Civil Lines Metro Station, North Exit",
            landmark_notes="Inside cardbox box placed by pedestrian",
            hospital_assigned=hospitals_objs[1],
            status="RECOVERED",
            first_aid_viewed=True,
            medical_notes="Wound cleaned with antiseptic and dressed. Kitten fed kitten formula. Safe for adoption.",
        )
        RescueStatusLog.objects.create(
            report=rep2,
            status="REPORTED",
            message="Initial report logged."
        )
        RescueStatusLog.objects.create(
            report=rep2,
            status="RECOVERED",
            message="Patient treated successfully and transferred to foster care."
        )

        print("✅ Sample rescue reports and audit timeline created.")

    print("\n🎉 ResQPaws AI database is fully seeded and ready!")

if __name__ == '__main__':
    seed_database()
