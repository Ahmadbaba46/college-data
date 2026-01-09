from django.urls import path
from grading import views

app_name = 'grading'

urlpatterns = [
    # Enrollment management
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('enrollments/create/', views.enrollment_create, name='enrollment_create'),
    path('enrollments/bulk/', views.enrollment_bulk, name='enrollment_bulk'),
    
    # Grade entry (Teacher)
    path('grades/my-courses/', views.teacher_courses, name='teacher_courses'),
    path('grades/offering/<int:offering_id>/entry/', views.grade_entry, name='grade_entry'),
    path('grades/offering/<int:offering_id>/submit/', views.grade_submit, name='grade_submit'),
    
    # Grade approval (Admin)
    path('grades/approval-queue/', views.approval_queue, name='approval_queue'),
    path('grades/<int:grade_id>/approve/', views.grade_approve, name='grade_approve'),
    path('grades/<int:grade_id>/reject/', views.grade_reject, name='grade_reject'),
    
    # Reports
    path('reports/grade-history/', views.grade_history, name='grade_history'),
    path('reports/repeated-courses/', views.repeated_courses_report, name='repeated_courses_report'),
]
