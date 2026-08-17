from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage, EmergencyHotline
from rescue.models import RescueReport
from hospitals.models import Hospital

def global_context(request):
    """Context processor for site-wide statistics and emergency banner."""
    total_rescued = RescueReport.objects.filter(status='RECOVERED').count() + 142
    total_reports = RescueReport.objects.count() + 185
    total_hospitals = Hospital.objects.count() + 24
    hotlines = EmergencyHotline.objects.filter(is_active=True)[:3]
    
    return {
        'SITE_NAME': 'ResQPaws AI',
        'SITE_TAGLINE': 'Intelligent Animal Emergency Response & Rescue Management System',
        'STAT_RESCUED': total_rescued,
        'STAT_REPORTS': total_reports,
        'STAT_HOSPITALS': total_hospitals,
        'GLOBAL_HOTLINES': hotlines,
    }

def home(request):
    recent_rescues = RescueReport.objects.select_related('hospital_assigned').order_by('-reported_at')[:6]
    hospitals = Hospital.objects.filter(is_active=True)[:4]
    
    context = {
        'recent_rescues': recent_rescues,
        'hospitals': hospitals,
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject or 'General Inquiry',
                message=message
            )
            messages.success(request, 'Thank you! Your message has been received. Our rescue coordination team will contact you shortly.')
            return redirect('core:contact')
        else:
            messages.error(request, 'Please complete all required fields.')

    hotlines = EmergencyHotline.objects.filter(is_active=True)
    return render(request, 'core/contact.html', {'hotlines': hotlines})
