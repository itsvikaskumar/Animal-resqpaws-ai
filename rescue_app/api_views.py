import os
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import Hospital, EmergencyReport
from .ml_pipeline.yolo_detector import YOLOV8AnimalInjuryDetector
from .ml_pipeline.severity_engine import InjurySeverityEngine
from .ml_pipeline.llm_agent import LLMInformationAgent
from .views import haversine_distance


# =========================================================
# YOLO ENGINE
# =========================================================

yolo_engine = YOLOV8AnimalInjuryDetector()


# =========================================================
# IMAGE ANALYSIS API
# =========================================================

@csrf_exempt
def api_analyze_image(request):
    """
    Image upload
        ↓
    YOLOv8 detection
        ↓
    Severity calculation
        ↓
    Gemini first-aid guidance
    """

    if request.method != 'POST':
        return JsonResponse(
            {'error': 'POST request required'},
            status=400
        )

    image_file = request.FILES.get('image')

    if not image_file:
        return JsonResponse(
            {'error': 'No image file uploaded'},
            status=400
        )

    file_path = default_storage.save(
        f"temp/{image_file.name}",
        ContentFile(image_file.read())
    )

    full_path = default_storage.path(file_path)

    try:

        # =====================================================
        # YOLOv8 ANALYSIS
        # =====================================================

        analysis = yolo_engine.analyze(full_path)

        severity_code, severity_text = (
            InjurySeverityEngine.calculate_severity(analysis)
        )


        # =====================================================
        # GEMINI FIRST-AID GUIDANCE
        # =====================================================

        first_aid = LLMInformationAgent.generate_first_aid(
            analysis.get('animal_type', 'Unknown'),
            ", ".join(analysis.get('injuries', [])),
            severity_code
        )


        # =====================================================
        # PROCESSED IMAGE
        # =====================================================

        processed_rel_url = ""

        processed_path = analysis.get(
            'processed_image_path'
        )

        if processed_path and os.path.exists(processed_path):

            processed_rel_url = (
                f"/media/temp/"
                f"{os.path.basename(processed_path)}"
            )


        return JsonResponse({

            'success': True,

            'is_animal': analysis.get(
                'is_animal',
                False
            ),

            'animal_type': analysis.get(
                'animal_type',
                'Unknown'
            ),

            'injuries': analysis.get(
                'injuries',
                []
            ),

            'severity_code': severity_code,

            'severity_text': severity_text,

            'first_aid_guidance': first_aid,

            'processed_image_url': processed_rel_url,

            'temp_file_name': file_path
        })


    except Exception as e:

        print(f"[Image Analysis Error] {e}")

        return JsonResponse(
            {
                'success': False,
                'error': str(e)
            },
            status=500
        )


# =========================================================
# FIND NEAREST HOSPITAL
# =========================================================

@csrf_exempt
def api_find_nearest_shelter(request):
    """
    Find nearest active hospital using Haversine distance.
    """

    try:

        lat = float(
            request.GET.get(
                'lat',
                30.3165
            )
        )

        lng = float(
            request.GET.get(
                'lng',
                78.0322
            )
        )


        hospitals = Hospital.objects.filter(
            is_active=True
        )

        hospital_list = []


        for hospital in hospitals:

            distance = haversine_distance(
                lat,
                lng,
                hospital.latitude,
                hospital.longitude
            )

            hospital_list.append({

                'id': hospital.id,

                'name': hospital.name,

                'address': hospital.address,

                'city': hospital.city,

                'phone': hospital.phone,

                'whatsapp': (
                    hospital.whatsapp
                    or hospital.phone
                ),

                'email': hospital.email,

                'latitude': hospital.latitude,

                'longitude': hospital.longitude,

                'has_ambulance': (
                    hospital.has_ambulance
                ),

                'distance_km': distance
            })


        # Nearest first
        hospital_list.sort(
            key=lambda x: x['distance_km']
        )

        nearest = (
            hospital_list[0]
            if hospital_list
            else None
        )


        return JsonResponse({

            'success': True,

            'nearest': nearest,

            'all_nearby': hospital_list[:5]
        })


    except Exception as e:

        return JsonResponse(
            {
                'success': False,
                'error': str(e)
            },
            status=400
        )


# =========================================================
# SUBMIT EMERGENCY REPORT
# =========================================================

@csrf_exempt
def api_submit_emergency(request):
    """
    Submit emergency report.

    IMPORTANT:
    Ambulance is NOT automatically assigned here.

    Ambulance will only appear after an actual ambulance
    is assigned through the dispatch workflow.
    """

    if request.method != 'POST':

        return JsonResponse(
            {'error': 'POST required'},
            status=400
        )


    try:

        data = request.POST


        # =====================================================
        # LOCATION
        # =====================================================

        lat = float(
            data.get(
                'latitude',
                30.3165
            )
        )

        lng = float(
            data.get(
                'longitude',
                78.0322
            )
        )


        # =====================================================
        # FIND NEAREST HOSPITAL
        # =====================================================

        hospitals = list(
            Hospital.objects.filter(
                is_active=True
            )
        )


        hospitals.sort(
            key=lambda hospital:
            haversine_distance(
                lat,
                lng,
                hospital.latitude,
                hospital.longitude
            )
        )


        assigned_hospital = (
            hospitals[0]
            if hospitals
            else None
        )


        # =====================================================
        # SEVERITY
        # =====================================================

        severity = data.get(
            'apparent_severity',
            'UNKNOWN'
        )


        # =====================================================
        # STATUS
        # =====================================================

        # IMPORTANT:
        # Critical report does NOT mean ambulance already assigned.

        if severity == 'CRITICAL':

            initial_status = 'SEARCHING'

        else:

            initial_status = 'REPORTED'


        # =====================================================
        # CREATE REPORT
        # =====================================================

        report = EmergencyReport(

            reporter_name=data.get(
                'reporter_name',
                'Anonymous Samaritan'
            ),

            reporter_phone=data.get(
                'reporter_phone',
                'Not Provided'
            ),

            reporter_email=data.get(
                'reporter_email',
                'help@resqpaws.org'
            ),

            latitude=lat,

            longitude=lng,

            address_text=data.get(
                'address_text',
                ''
            ),

            is_animal_detected=(
                data.get(
                    'is_animal_detected'
                ) == 'true'
            ),

            detected_animal=data.get(
                'detected_animal',
                'Animal in distress'
            ),

            detected_injuries=data.get(
                'detected_injuries',
                'Emergency reported'
            ),

            apparent_severity=severity,

            ai_first_aid_guidance=data.get(
                'ai_first_aid_guidance',
                ''
            ),

            assigned_hospital=assigned_hospital,

            status=initial_status,

            # NO ambulance assignment here
            ambulance_assigned=False,

            ambulance_lat=None,

            ambulance_lng=None,

            eta_minutes=15
        )


        # =====================================================
        # IMAGE
        # =====================================================

        if 'image' in request.FILES:

            report.image = request.FILES['image']


        # =====================================================
        # SAVE
        # =====================================================

        report.save()


        # =====================================================
        # RESPONSE
        # =====================================================

        return JsonResponse({

            'success': True,

            'report_id': str(
                report.report_id
            ),

            'short_id': str(
                report.report_id
            )[:8],

            'status': report.status,

            'hospital_name': (
                assigned_hospital.name
                if assigned_hospital
                else 'Central Rescue Network'
            ),

            'hospital_phone': (
                assigned_hospital.phone
                if assigned_hospital
                else '112'
            ),

            'hospital_whatsapp': (
                assigned_hospital.whatsapp
                if assigned_hospital
                else ''
            ),

            'ambulance_assigned': False,

            'eta': report.eta_minutes
        })


    except Exception as e:

        print(f"[Emergency Submit Error] {e}")

        return JsonResponse(
            {
                'success': False,
                'error': str(e)
            },
            status=500
        )


# =========================================================
# GEMINI AI CHAT API
# =========================================================

@csrf_exempt
def api_chat_message(request):
    """
    ResQPaws AI Chat API.

    User message
        ↓
    Django
        ↓
    Conversation history
        ↓
    Gemini
        ↓
    AI response
    """

    if request.method != 'POST':

        return JsonResponse(
            {'error': 'POST required'},
            status=400
        )


    try:

        # =====================================================
        # READ REQUEST
        # =====================================================

        body = json.loads(
            request.body.decode('utf-8')
        )

        user_text = str(
            body.get(
                'message',
                ''
            )
        ).strip()


        if not user_text:

            return JsonResponse(
                {
                    'success': False,
                    'error': 'Message is required'
                },
                status=400
            )


        # =====================================================
        # GET PREVIOUS CONVERSATION
        # =====================================================

        chat_history = request.session.get(
            'resqpaws_chat_history',
            []
        )


        # =====================================================
        # BUILD CONTEXT
        # =====================================================

        context_parts = []

        for message in chat_history[-10:]:

            role = message.get(
                'role',
                'user'
            )

            text = message.get(
                'text',
                ''
            )

            if text:

                if role == 'user':

                    context_parts.append(
                        f"User: {text}"
                    )

                else:

                    context_parts.append(
                        f"ResQPaws AI: {text}"
                    )


        context = "\n".join(
            context_parts
        )


        # =====================================================
        # ASK GEMINI
        # =====================================================

        bot_reply = (
            LLMInformationAgent.chat_response(
                user_message=user_text,
                context=context
            )
        )


        # =====================================================
        # SAVE CONVERSATION
        # =====================================================

        chat_history.append({

            'role': 'user',

            'text': user_text
        })


        chat_history.append({

            'role': 'assistant',

            'text': bot_reply
        })


        # Keep last 20 messages
        request.session[
            'resqpaws_chat_history'
        ] = chat_history[-20:]


        request.session.modified = True


        # =====================================================
        # RESPONSE
        # =====================================================

        return JsonResponse({

            'success': True,

            'reply': bot_reply
        })


    except json.JSONDecodeError:

        return JsonResponse(
            {
                'success': False,
                'error': 'Invalid JSON request'
            },
            status=400
        )


    except Exception as e:

        print(f"[Chat API Error] {e}")

        return JsonResponse(
            {
                'success': False,
                'error': str(e)
            },
            status=500
        )


# =========================================================
# CLEAR CHAT HISTORY
# =========================================================

@csrf_exempt
def api_clear_chat(request):
    """
    Clears the current user's ResQPaws AI conversation.
    """

    if request.method != 'POST':

        return JsonResponse(
            {'error': 'POST required'},
            status=400
        )


    request.session[
        'resqpaws_chat_history'
    ] = []

    request.session.modified = True


    return JsonResponse({

        'success': True,

        'message': 'Chat history cleared'
    })


# =========================================================
# LIVE AMBULANCE TRACKING
# =========================================================

def api_get_live_tracking(request, report_id):
    """
    Returns live ambulance coordinates.

    If no ambulance is assigned:
        ambulance_assigned = False
        ambulance coordinates = None
    """

    report = EmergencyReport.objects.filter(
        report_id__startswith=report_id
    ).first()


    if not report:

        return JsonResponse(
            {
                'error': 'Report not found'
            },
            status=404
        )


    # =====================================================
    # AMBULANCE INFORMATION
    # =====================================================

    ambulance = report.assigned_ambulance


    if (
        ambulance
        and report.ambulance_assigned
    ):

        ambulance_assigned = True

        ambulance_lat = (
            report.ambulance_lat
            if report.ambulance_lat is not None
            else ambulance.latitude
        )

        ambulance_lng = (
            report.ambulance_lng
            if report.ambulance_lng is not None
            else ambulance.longitude
        )

        driver_name = ambulance.driver_name

        driver_phone = ambulance.driver_phone

    else:

        ambulance_assigned = False

        ambulance_lat = None

        ambulance_lng = None

        driver_name = ''

        driver_phone = ''


    # =====================================================
    # RESPONSE
    # =====================================================

    return JsonResponse({

        'report_id': str(
            report.report_id
        )[:8],

        'status': report.status,

        'status_display': (
            report.get_status_display()
        ),

        'animal': report.detected_animal,

        'severity': report.apparent_severity,

        'animal_lat': report.latitude,

        'animal_lng': report.longitude,

        'ambulance_assigned': (
            ambulance_assigned
        ),

        'ambulance_lat': (
            ambulance_lat
        ),

        'ambulance_lng': (
            ambulance_lng
        ),

        'driver_name': driver_name,

        'driver_phone': driver_phone,

        'eta_minutes': report.eta_minutes,

        'hospital_name': (
            report.assigned_hospital.name
            if report.assigned_hospital
            else 'Central Rescue Facility'
        ),

        'hospital_phone': (
            report.assigned_hospital.phone
            if report.assigned_hospital
            else '112'
        ),

        'hospital_whatsapp': (
            report.assigned_hospital.whatsapp
            if report.assigned_hospital
            else ''
        )
    })