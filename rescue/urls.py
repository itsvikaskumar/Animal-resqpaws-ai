from django.urls import path
from . import views

app_name = 'rescue'

urlpatterns = [
    path('report/', views.report_animal, name='report_animal'),
    path('ai-result/<str:tracking_id>/', views.ai_result, name='ai_result'),
    path('first-aid/', views.first_aid_view, name='first_aid'),
    path('first-aid/<str:tracking_id>/', views.first_aid_view, name='first_aid_case'),
    path('track/<str:tracking_id>/', views.track_rescue, name='track_rescue'),
    path('my-rescues/', views.user_dashboard, name='user_dashboard'),
    path('api/track/<str:tracking_id>/', views.api_track_status, name='api_track_status'),
]
