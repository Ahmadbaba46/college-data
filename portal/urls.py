from django.urls import path
from portal import views

app_name = 'portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('partials/system-stats/', views.system_stats_partial, name='system_stats_partial'),
    
    # Chart data API endpoints
    path('api/enrollment-stats/', views.enrollment_stats_data, name='enrollment_stats_data'),
    path('api/student-distribution/', views.student_distribution_data, name='student_distribution_data'),
    path('api/grade-distribution/', views.grade_distribution_data, name='grade_distribution_data'),
    
    # Activity feed
    path('partials/recent-activity/', views.recent_activity_partial, name='recent_activity_partial'),
    
    # Dashboard widgets
    path('partials/repeated-courses-alert/', views.repeated_courses_alert_partial, name='repeated_courses_alert_partial'),
    path('partials/graduation-eligibility/', views.graduation_eligibility_partial, name='graduation_eligibility_partial'),
]
