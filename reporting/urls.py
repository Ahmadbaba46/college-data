"""
URL Configuration for Transcript Reporting Module
===============================================

This module defines URL patterns for:
1. Web-based transcript verification
2. REST API endpoints
3. File download endpoints
4. API documentation
"""

from django.urls import path, include
from . import views

app_name = 'reporting'

# Web interface URLs
web_urlpatterns = [
    path('verify/', views.TranscriptVerificationView.as_view(), name='verify_transcript'),
    path('transcripts/generate/', views.transcript_generate, name='transcript_generate'),
    path('transcripts/batch/', views.transcript_batch, name='transcript_batch'),
    path('transcripts/history/', views.transcript_history, name='transcript_history'),
]

# API URLs
api_urlpatterns = [
    # Transcript operations
    path('transcripts/', views.TranscriptAPIView.as_view(), name='api_transcript_list'),
    path('transcripts/<str:student_id>/', views.TranscriptAPIView.as_view(), name='api_transcript_detail'),
    path('transcripts/download/<str:filename>/', views.download_transcript, name='api_transcript_download'),
    
    # Verification
    path('verify/', views.VerificationAPIView.as_view(), name='api_verify_list'),
    path('verify/<str:verification_code>/', views.VerificationAPIView.as_view(), name='api_verify_detail'),
]

urlpatterns = [
    # Web interface
    path('', include(web_urlpatterns)),
    
    # API endpoints
    path('api/', include(api_urlpatterns)),
]