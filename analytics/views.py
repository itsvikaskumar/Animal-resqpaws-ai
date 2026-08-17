import json
from django.shortcuts import render
from django.db.models import Count, Q
from accounts.decorators import admin_required
from rescue.models import RescueReport, RescueStatusLog
from hospitals.models import Hospital, Ambulance
from django.contrib.auth.models import User

@admin_required
def admin_dashboard(request):
    # Core KPIs
    total_reports = RescueReport.objects.count()
    active_emergencies = RescueReport.objects.exclude(status__in=['RECOVERED', 'CLOSED']).count()
    successful_rescues = RescueReport.objects.filter(status__in=['RESCUED', 'IN_TREATMENT', 'RECOVERED']).count()
    critical_cases = RescueReport.objects.filter(injury_severity='CRITICAL').count()

    total_hospitals = Hospital.objects.filter(is_active=True).count()
    total_ambulances = Ambulance.objects.count()
    active_ambulances = Ambulance.objects.filter(status__in=['DISPATCHED', 'ON_SCENE', 'RETURNING']).count()
    registered_users = User.objects.count()

    # Species Breakdown
    species_counts = RescueReport.objects.values('species').annotate(count=Count('id')).order_by('-count')
    species_labels = [dict(RescueReport.SPECIES_CHOICES).get(item['species'], item['species']) for item in species_counts]
    species_data = [item['count'] for item in species_counts]

    # Severity Breakdown
    severity_counts = RescueReport.objects.values('injury_severity').annotate(count=Count('id'))
    severity_dict = {item['injury_severity']: item['count'] for item in severity_counts}
    severity_labels = ['Critical', 'Severe', 'Moderate', 'Minor']
    severity_data = [
        severity_dict.get('CRITICAL', 0),
        severity_dict.get('SEVERE', 0),
        severity_dict.get('MODERATE', 0),
        severity_dict.get('MINOR', 0)
    ]

    # Hospital performance
    hospitals = Hospital.objects.annotate(
        total_assigned=Count('assigned_reports'),
        resolved_count=Count('assigned_reports', filter=Q(assigned_reports__status='RECOVERED'))
    ).order_by('-total_assigned')[:8]

    # Recent Audit Logs
    recent_logs = RescueStatusLog.objects.select_related('report', 'updated_by').order_by('-timestamp')[:10]
    recent_reports = RescueReport.objects.select_related('hospital_assigned', 'ambulance_assigned').order_by('-reported_at')[:8]

    context = {
        'total_reports': total_reports,
        'active_emergencies': active_emergencies,
        'successful_rescues': successful_rescues,
        'critical_cases': critical_cases,
        'total_hospitals': total_hospitals,
        'total_ambulances': total_ambulances,
        'active_ambulances': active_ambulances,
        'registered_users': registered_users,
        
        # Charts Data in JSON
        'species_labels_json': json.dumps(species_labels),
        'species_data_json': json.dumps(species_data),
        'severity_labels_json': json.dumps(severity_labels),
        'severity_data_json': json.dumps(severity_data),

        'hospitals': hospitals,
        'recent_logs': recent_logs,
        'recent_reports': recent_reports,
    }
    return render(request, 'analytics/admin_dashboard.html', context)
