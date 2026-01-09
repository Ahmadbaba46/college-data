from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_overview, name='overview'),
    path('enrollments/', views.enrollment_analytics, name='enrollments'),
    path('students/', views.student_analytics, name='students'),
    path('grades/', views.grade_analytics, name='grades'),
    path('teachers/', views.teacher_analytics, name='teachers'),
    path('graduation/', views.graduation_analytics, name='graduation'),
    
    # Exports
    path('export/enrollments/', views.export_enrollments, name='export_enrollments'),
    path('export/students/', views.export_students, name='export_students'),
    path('export/grades/', views.export_grades, name='export_grades'),
    path('export/teachers/', views.export_teachers, name='export_teachers'),
    path('export/graduation/', views.export_graduation, name='export_graduation'),
]
