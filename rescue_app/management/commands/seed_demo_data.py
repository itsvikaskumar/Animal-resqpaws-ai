from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rescue_app.models import Hospital, HospitalStaff, EmergencyReport

class Command(BaseCommand):
    help = 'Populates demo hospitals (Dehradun / Uttarakhand), staff accounts and test reports'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding ResQPaws demo data...")

        # 1. Create Demo Hospitals in Dehradun / Uttarakhand region (as in synopsis)
        hospitals_data = [
            {
                'name': 'Government Veterinary Hospital & Trauma Centre',
                'address': 'Chakrata Road, Near Bindal Bridge',
                'city': 'Dehradun',
                'phone': '+91 94120 12345',
                'whatsapp': '+919412012345',
                'email': 'gvh.dehradun@resqpaws.org',
                'latitude': 30.3244,
                'longitude': 78.0339,
                'has_ambulance': True
            },
            {
                'name': 'Dev Bhoomi Animal Rescue & Care Centre',
                'address': 'Navgaon, Manduwala',
                'city': 'Dehradun',
                'phone': '+91 98970 88776',
                'whatsapp': '+919897088776',
                'email': 'rescue@dbuu.ac.in',
                'latitude': 30.3551,
                'longitude': 77.9482,
                'has_ambulance': True
            },
            {
                'name': 'Doon Paws Veterinary Clinic & Shelter',
                'address': 'Rajpur Road, Near Clock Tower',
                'city': 'Dehradun',
                'phone': '+91 97561 22334',
                'whatsapp': '+919756122334',
                'email': 'doonpaws@resqpaws.org',
                'latitude': 30.3165,
                'longitude': 78.0322,
                'has_ambulance': True
            },
            {
                'name': 'Rishikesh Animal Welfare Emergency Hospital',
                'address': 'Tapovan, Badrinath Road',
                'city': 'Rishikesh',
                'phone': '+91 94111 99887',
                'whatsapp': '+919411199887',
                'email': 'rishikesh.vet@resqpaws.org',
                'latitude': 30.1256,
                'longitude': 78.3189,
                'has_ambulance': True
            }
        ]

        created_hospitals = []
        for h in hospitals_data:
            obj, _ = Hospital.objects.get_or_create(name=h['name'], defaults=h)
            created_hospitals.append(obj)

        # 2. Create Staff User
        staff_user, created = User.objects.get_or_create(
            username='hospital_admin',
            defaults={
                'email': 'staff@gvh.org',
                'first_name': 'Dr. Alok',
                'last_name': 'Verma',
                'is_staff': True
            }
        )
        if created:
            staff_user.set_password('admin123')
            staff_user.save()
            HospitalStaff.objects.create(
                user=staff_user,
                hospital=created_hospitals[0],
                phone='+91 94120 12345'
            )

        # 3. Create Sample Emergency Report
        EmergencyReport.objects.get_or_create(
            reporter_name='Atrish Thapliyal',
            reporter_phone='+91 98765 00001',
            reporter_email='atrish@dbuu.ac.in',
            latitude=30.3240,
            longitude=78.0340,
            address_text='Near Bindal Bridge Roadside',
            is_animal_detected=True,
            detected_animal='Dog',
            detected_injuries='Visible Bleeding & Open Leg Wound',
            apparent_severity='CRITICAL',
            ai_first_aid_guidance='1. Direct gentle pressure applied with sterile cloth.\n2. Keep warm and quiet.\n3. Ambulance dispatched with trauma kit.',
            assigned_hospital=created_hospitals[0],
            status='DISPATCHED',
            ambulance_assigned=True,
            ambulance_driver_name='Rahul Sharma',
            ambulance_driver_phone='+91 98765 43210',
            ambulance_lat=30.3150,
            ambulance_lng=78.0280,
            eta_minutes=8
        )

        self.stdout.write(self.style.SUCCESS("Demo hospitals, hospital staff ('hospital_admin' / 'admin123'), and test cases successfully created!"))