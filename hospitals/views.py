from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import hospital_staff_required
from .models import Hospital, Ambulance
from .forms import AmbulanceForm
from rescue.models import RescueReport, RescueStatusLog
from rescue.utils import haversine_distance

@hospital_staff_required
def hospital_dashboard(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Determine the active hospital for this staff member
    if user.is_superuser or not profile or not profile.affiliated_hospital:
        hospital = Hospital.objects.filter(is_active=True).first()
    else:
        hospital = profile.affiliated_hospital

    if not hospital:
        messages.warning(request, "No hospital is currently configured. Please contact the administrator.")
        return redirect('core:home')

    # Query incoming and ongoing rescue reports
    assigned_reports = RescueReport.objects.filter(hospital_assigned=hospital).order_by('-reported_at')
    
    critical_cases = assigned_reports.filter(injury_severity__in=['CRITICAL', 'SEVERE']).exclude(status__in=['RECOVERED', 'CLOSED'])
    pending_dispatch = assigned_reports.filter(status='ASSIGNED')
    active_rescues = assigned_reports.filter(status__in=['DISPATCHED', 'ON_SCENE', 'RESCUED'])
    admitted_patients = assigned_reports.filter(status='IN_TREATMENT')

    ambulances = hospital.ambulances.all()
    available_ambulances = ambulances.filter(status='AVAILABLE')

    all_hospitals = Hospital.objects.filter(is_active=True) if user.is_superuser else [hospital]

    context = {
        'hospital': hospital,
        'all_hospitals': all_hospitals,
        'assigned_reports': assigned_reports[:12],
        'critical_cases': critical_cases,
        'pending_dispatch': pending_dispatch,
        'active_rescues': active_rescues,
        'admitted_patients': admitted_patients,
        'ambulances': ambulances,
        'available_ambulances': available_ambulances,
    }
    return render(request, 'hospitals/dashboard.html', context)


@hospital_staff_required
def report_detail(request, report_id):
    report = get_object_or_404(RescueReport, id=report_id)
    hospital = report.hospital_assigned

    # Calculate distance
    distance_km = None
    if hospital:
        distance_km = haversine_distance(report.latitude, report.longitude, hospital.latitude, hospital.longitude)

    available_ambulances = hospital.ambulances.filter(status='AVAILABLE') if hospital else Ambulance.objects.filter(status='AVAILABLE')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'dispatch':
            ambulance_id = request.POST.get('ambulance_id')
            if ambulance_id:
                ambulance = get_object_or_404(Ambulance, id=ambulance_id)
                ambulance.status = 'DISPATCHED'
                ambulance.save()

                report.ambulance_assigned = ambulance
                report.status = 'DISPATCHED'
                report.save()

                RescueStatusLog.objects.create(
                    report=report,
                    status='DISPATCHED',
                    message=f"Ambulance {ambulance.vehicle_number} (Driver: {ambulance.driver_name}, Ph: {ambulance.driver_phone}) dispatched to location.",
                    updated_by=request.user
                )
                messages.success(request, f"🚑 Ambulance {ambulance.vehicle_number} dispatched successfully!")
            else:
                messages.error(request, "Please select an available ambulance to dispatch.")

        elif action == 'update_status':
            new_status = request.POST.get('status')
            notes = request.POST.get('medical_notes', '').strip()
            
            if new_status in dict(RescueReport.STATUS_CHOICES):
                report.status = new_status
                if notes:
                    report.medical_notes = notes
                
                # Check recovery photo upload
                if 'recovery_photo' in request.FILES:
                    report.recovery_photo = request.FILES['recovery_photo']

                # Release ambulance back to AVAILABLE if rescued or admitted
                if new_status in ['IN_TREATMENT', 'RECOVERED', 'CLOSED'] and report.ambulance_assigned:
                    amb = report.ambulance_assigned
                    amb.status = 'AVAILABLE'
                    amb.save()

                # Update hospital occupancy
                if new_status == 'IN_TREATMENT' and hospital:
                    hospital.current_occupancy = min(hospital.capacity, hospital.current_occupancy + 1)
                    hospital.save()
                elif new_status in ['RECOVERED', 'CLOSED'] and hospital:
                    hospital.current_occupancy = max(0, hospital.current_occupancy - 1)
                    hospital.save()

                report.save()

                RescueStatusLog.objects.create(
                    report=report,
                    status=new_status,
                    message=f"Status updated to {report.get_status_display()}. Notes: {notes or 'No clinical remarks'}",
                    updated_by=request.user
                )
                messages.success(request, f"Report status updated to: {report.get_status_display()}")

        return redirect('hospitals:report_detail', report_id=report.id)

    context = {
        'report': report,
        'distance_km': distance_km,
        'available_ambulances': available_ambulances,
        'logs': report.status_logs.all(),
        'status_choices': RescueReport.STATUS_CHOICES,
    }
    return render(request, 'hospitals/report_detail.html', context)


@hospital_staff_required
def ambulance_management(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    
    if user.is_superuser or not profile or not profile.affiliated_hospital:
        hospital = Hospital.objects.filter(is_active=True).first()
    else:
        hospital = profile.affiliated_hospital

    if not hospital:
        messages.warning(request, "No hospital is currently configured.")
        return redirect('core:home')

    if request.method == 'POST':
        form = AmbulanceForm(request.POST)
        if form.is_valid():
            ambulance = form.save(commit=False)
            ambulance.hospital = hospital
            ambulance.save()
            messages.success(request, f"Ambulance {ambulance.vehicle_number} registered to {hospital.name} fleet.")
            return redirect('hospitals:ambulance_management')
        else:
            messages.error(request, "Please check the ambulance details provided.")
    else:
        form = AmbulanceForm()

    ambulances = hospital.ambulances.all()

    context = {
        'hospital': hospital,
        'ambulances': ambulances,
        'form': form,
    }
    return render(request, 'hospitals/ambulance_management.html', context)
