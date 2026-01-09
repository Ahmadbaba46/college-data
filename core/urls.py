from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Sessions
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/create/', views.session_create, name='session_create'),
    path('sessions/<int:session_id>/edit/', views.session_edit, name='session_edit'),
    path('sessions/<int:session_id>/delete/', views.session_delete, name='session_delete'),
    path('sessions/<int:session_id>/set-current/', views.session_set_current, name='session_set_current'),
    
    # Levels
    path('levels/', views.level_list, name='level_list'),
    path('levels/create/', views.level_create, name='level_create'),
    path('levels/<int:level_id>/edit/', views.level_edit, name='level_edit'),
    path('levels/<int:level_id>/delete/', views.level_delete, name='level_delete'),
    
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:department_id>/', views.department_detail, name='department_detail'),
    path('departments/<int:department_id>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:department_id>/delete/', views.department_delete, name='department_delete'),
    
    # College Settings
    path('college/', views.college_settings, name='college_settings'),
    
    # Academic Policy
    path('academic-policy/', views.academic_policy_settings, name='academic_policy_settings'),
    
    # Grading Settings
    path('grading/', views.grading_settings, name='grading_settings'),
    path('grading/create/', views.grading_settings_create, name='grading_settings_create'),
    path('grading/<int:grade_id>/edit/', views.grading_settings_edit, name='grading_settings_edit'),
    path('grading/<int:grade_id>/delete/', views.grading_settings_delete, name='grading_settings_delete'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    
    # Audit Log
    path('audit-log/', views.audit_log, name='audit_log'),
    path('audit-log/export/', views.audit_log_export, name='audit_log_export'),
]
