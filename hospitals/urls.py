from django.urls import path
from . import views

app_name = 'hospitals'

urlpatterns = [
    path('dashboard/', views.hospital_dashboard, name='dashboard'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('ambulances/', views.ambulance_management, name='ambulance_management'),
]
