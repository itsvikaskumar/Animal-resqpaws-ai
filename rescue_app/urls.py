from django.urls import path
from . import views, api_views


urlpatterns = [

    # =========================================================
    # PAGES
    # =========================================================

    path(
        '',
        views.home_view,
        name='home'
    ),

    path(
        'about/',
        views.about_view,
        name='about'
    ),

    path(
        'first-aid/',
        views.first_aid_view,
        name='first_aid'
    ),

    path(
        'contact/',
        views.contact_view,
        name='contact'
    ),

    path(
        'report-emergency/',
        views.report_emergency_view,
        name='report_emergency'
    ),

    path(
        'track-report/',
        views.track_report_view,
        name='track_report'
    ),

    path(
        'hospital-dashboard/',
        views.hospital_dashboard_view,
        name='hospital_dashboard'
    ),

    path(
        'hospital-dashboard/update/<uuid:report_id>/',
        views.update_case_status_view,
        name='update_case_status'
    ),


    # =========================================================
    # AUTHENTICATION
    # =========================================================

    path(
        'register/',
        views.user_register_view,
        name='register'
    ),

    path(
        'login/',
        views.user_login_view,
        name='login'
    ),

    path(
        'logout/',
        views.user_logout_view,
        name='logout'
    ),


    # =========================================================
    # REST / AJAX API ENDPOINTS
    # =========================================================

    # AI / YOLO Image Analysis
    path(
        'api/analyze-image/',
        api_views.api_analyze_image,
        name='api_analyze_image'
    ),

    # Find Nearest Rescue Center / Hospital
    path(
        'api/find-nearest-shelter/',
        api_views.api_find_nearest_shelter,
        name='api_find_nearest_shelter'
    ),

    # Submit Animal Emergency
    path(
        'api/submit-emergency/',
        api_views.api_submit_emergency,
        name='api_submit_emergency'
    ),


    # =========================================================
    # RESQPAWS AI CHAT
    # =========================================================

    # Send message to ResQPaws AI / Gemini
    path(
        'api/chat/',
        api_views.api_chat_message,
        name='api_chat_message'
    ),

    # Clear ResQPaws AI chat history
    path(
        'api/chat/clear/',
        api_views.api_clear_chat,
        name='api_clear_chat'
    ),


    # =========================================================
    # LIVE AMBULANCE TRACKING
    # =========================================================

    path(
        'api/tracking/<str:report_id>/',
        api_views.api_get_live_tracking,
        name='api_live_tracking'
    ),
]