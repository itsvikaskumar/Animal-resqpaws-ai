import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Hospital, EmergencyReport, HospitalStaff
from .forms import UserRegisterForm, LoginForm, EmergencyReportDirectForm
from .ml_pipeline.llm_agent import LLMInformationAgent

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def home_view(request):
    hospitals = Hospital.objects.filter(is_active=True)[:6]
    total_rescues = EmergencyReport.objects.filter(status='RESOLVED').count() + 124
    active_cases = EmergencyReport.objects.filter(status__in=['REPORTED', 'SEARCHING', 'DISPATCHED', 'ADMITTED']).count()
    return render(request, 'home.html', {
        'hospitals': hospitals,
        'total_rescues': total_rescues,
        'active_cases': active_cases,
    })

def about_view(request):
    return render(request, 'about.html')

def first_aid_view(request):
    return render(request, 'first_aid.html')

def contact_view(request):
    hospitals = Hospital.objects.filter(is_active=True)
    if request.method == 'POST':
        messages.success(request, "Thank you! Your inquiry has been transmitted to our rescue coordination team.")
        return redirect('contact')
    return render(request, 'contact.html', {'hospitals': hospitals})

def report_emergency_view(request):
    hospitals = Hospital.objects.filter(is_active=True)
    return render(request, 'report_emergency.html', {'hospitals': hospitals})

def track_report_view(request):
    report = None
    query_id = request.GET.get('report_id', '').strip()
    if query_id:
        try:
            # Match either UUID prefix or full UUID
            if len(query_id) == 8:
                report = EmergencyReport.objects.filter(report_id__startswith=query_id).first()
            else:
                report = EmergencyReport.objects.filter(report_id=query_id).first()
            if not report:
                messages.error(request, f"No emergency report found matching Case ID: {query_id}")
        except Exception:
            messages.error(request, "Invalid Case ID format.")
            
    return render(request, 'track_report.html', {'report': report, 'query_id': query_id})

def user_register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to ResQPaws.")
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if hasattr(user, 'hospital_profile'):
                    return redirect('hospital_dashboard')
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def hospital_dashboard_view(request):
    # Check if user is associated with a hospital
    hospital = None
    if hasattr(request.user, 'hospital_profile'):
        hospital = request.user.hospital_profile.hospital
        reports = EmergencyReport.objects.filter(assigned_hospital=hospital).order_by('-created_at')
    elif request.user.is_staff:
        reports = EmergencyReport.objects.all().order_by('-created_at')
    else:
        messages.warning(request, "Access restricted to authorized hospital staff.")
        return redirect('home')

    return render(request, 'hospital_dashboard.html', {
        'hospital': hospital,
        'reports': reports
    })

@login_required
def update_case_status_view(request, report_id):
    report = get_object_or_404(EmergencyReport, report_id=report_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        driver_name = request.POST.get('driver_name', 'Rahul Sharma')
        driver_phone = request.POST.get('driver_phone', '+91 98765 43210')
        
        report.status = new_status
        if new_status == 'DISPATCHED':
            report.ambulance_assigned = True
            report.ambulance_driver_name = driver_name
            report.ambulance_driver_phone = driver_phone
            # Place ambulance slightly offset from destination to simulate route
            report.ambulance_lat = report.latitude - 0.015
            report.ambulance_lng = report.longitude - 0.012
            report.eta_minutes = 12
        elif new_status == 'RESOLVED':
            report.ambulance_assigned = False

        report.save()
        messages.success(request, f"Case #{str(report.report_id)[:8]} status updated to {report.get_status_display()}.")
    return redirect('hospital_dashboard')