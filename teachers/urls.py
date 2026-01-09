from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.teacher_list, name='list'),
    path('create/', views.teacher_create, name='create'),
    path('<int:teacher_id>/', views.teacher_detail, name='detail'),
    path('<int:teacher_id>/edit/', views.teacher_edit, name='edit'),
    path('<int:teacher_id>/delete/', views.teacher_delete, name='delete'),
    path('<int:teacher_id>/assign-courses/', views.assign_courses, name='assign_courses'),
]
