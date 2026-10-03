from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import RescueReport, RescueStatusLog
from .forms import RescueReportForm
from .utils import find_nearest_hospital, send_emergency_alert
from ai_engine.vision_analyzer import analyze_animal_image
from ai_engine.first_aid_data import get_first_aid_guide, SPECIES_FIRST_AID, SEVERITY_PROTOCOLS
from hospitals.models import Hospital

def report_animal(request):
    if request.method == 'POST':
        form = RescueReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            
            # Default coordinates if GPS unavailable on client
            if not report.latitude or not report.longitude:
                report.latitude = 28.6139  # Default City Center
                report.longitude = 77.2090

            if request.user.is_authenticated:
                report.reporter = request.user
                if not report.reporter_name:
                    report.reporter_name = request.user.get_full_name() or request.user.username

            report.save()

            # Execute AI Vision Diagnostics on the uploaded animal photo
            if report.image:
                ai_data = analyze_animal_image(report.image.path, report.species)
                report.species_detected_by_ai = ai_data.get('species_name', report.get_species_display())
                report.injury_severity = ai_data.get('injury_severity', 'MODERATE')
                report.ai_confidence = ai_data.get('confidence', 90.0)
                report.ai_symptoms = " | ".join(ai_data.get('symptoms', []))
                report.annotated_image = ai_data.get('annotated_image', '')

            # Allocate nearest Hospital using Haversine calculation
            nearest_hosp, dist_km = find_nearest_hospital(report.latitude, report.longitude)
            if nearest_hosp:
                report.hospital_assigned = nearest_hosp
                report.status = 'ASSIGNED'
                report.save()

                RescueStatusLog.objects.create(
                    report=report,
                    status='ASSIGNED',
                    message=f"AI identified {report.injury_severity} trauma. Case assigned to nearest center: {nearest_hosp.name} ({dist_km} km away)."
                )
                send_emergency_alert(report)
            else:
                report.status = 'REPORTED'
                report.save()
                RescueStatusLog.objects.create(
                    report=report,
                    status='REPORTED',
                    message="Case registered. Pending hospital routing queue."
                )

            messages.success(request, f"🚨 Emergency Report Filed! Case ID: {report.tracking_id}")
            return redirect('rescue:ai_result', tracking_id=report.tracking_id)
        else:
            messages.error(request, "Please check the form fields and upload a clear photo of the injured animal.")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['reporter_name'] = request.user.get_full_name() or request.user.username
            profile = getattr(request.user, 'profile', None)
            if profile and profile.phone:
                initial['reporter_phone'] = profile.phone
        form = RescueReportForm(initial=initial)

    hospitals_json = list(Hospital.objects.filter(is_active=True).values('id', 'name', 'latitude', 'longitude', 'phone', 'address'))
    return render(request, 'rescue/report_animal.html', {'form': form, 'hospitals_json': hospitals_json})


def ai_result(request, tracking_id):
    report = get_object_or_404(RescueReport, tracking_id=tracking_id)
    first_aid_snippet = get_first_aid_guide(report.species, report.injury_severity)
    
    # Calculate distance to assigned hospital
    distance_km = None
    if report.hospital_assigned:
        from .utils import haversine_distance
        distance_km = haversine_distance(
            report.latitude, report.longitude,
            report.hospital_assigned.latitude, report.hospital_assigned.longitude
        )

    context = {
        'report': report,
        'first_aid_snippet': first_aid_snippet,
        'distance_km': distance_km,
    }
    return render(request, 'rescue/ai_result.html', context)


def first_aid_view(request, tracking_id=None):
    report = None
    selected_species = request.GET.get('species', 'DOG')
    selected_severity = request.GET.get('severity', 'MODERATE')

    if tracking_id:
        report = get_object_or_404(RescueReport, tracking_id=tracking_id)
        selected_species = report.species
        selected_severity = report.injury_severity
        if not report.first_aid_viewed:
            report.first_aid_viewed = True
            report.save(update_fields=['first_aid_viewed'])

    guide = get_first_aid_guide(selected_species, selected_severity)

    context = {
        'report': report,
        'selected_species': selected_species,
        'selected_severity': selected_severity,
        'guide': guide,
        'species_list': SPECIES_FIRST_AID,
        'severity_list': SEVERITY_PROTOCOLS,
    }
    return render(request, 'rescue/first_aid.html', context)


def track_rescue(request, tracking_id):
    report = get_object_or_404(RescueReport, tracking_id=tracking_id)
    logs = report.status_logs.all()

    # Step progress integer (0 to 100%)
    status_weights = {
        'REPORTED': 15,
        'ASSIGNED': 30,
        'DISPATCHED': 55,
        'ON_SCENE': 75,
        'RESCUED': 90,
        'IN_TREATMENT': 95,
        'RECOVERED': 100,
        'CLOSED': 100,
    }
    progress_pct = status_weights.get(report.status, 20)

    context = {
        'report': report,
        'logs': logs,
        'progress_pct': progress_pct,
    }
    return render(request, 'rescue/track_rescue.html', context)


@login_required
def user_dashboard(request):
    reports = RescueReport.objects.filter(reporter=request.user).order_by('-reported_at')
    
    total_reported = reports.count()
    total_rescued = reports.filter(status__in=['RESCUED', 'IN_TREATMENT', 'RECOVERED']).count()
    active_cases = reports.exclude(status__in=['RECOVERED', 'CLOSED']).count()

    context = {
        'reports': reports,
        'total_reported': total_reported,
        'total_rescued': total_rescued,
        'active_cases': active_cases,
    }
    return render(request, 'rescue/user_dashboard.html', context)


def api_track_status(request, tracking_id):
    """API endpoint for live ajax polling on track page."""
    report = get_object_or_404(RescueReport, tracking_id=tracking_id)
    return JsonResponse({
        'tracking_id': report.tracking_id,
        'status': report.status,
        'status_display': report.get_status_display(),
        'severity': report.injury_severity,
        'ambulance_dispatched': bool(report.ambulance_assigned),
        'ambulance_number': report.ambulance_assigned.vehicle_number if report.ambulance_assigned else None,
        'driver_name': report.ambulance_assigned.driver_name if report.ambulance_assigned else None,
        'driver_phone': report.ambulance_assigned.driver_phone if report.ambulance_assigned else None,
    })
