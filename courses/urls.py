from django.urls import path
from courses import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('<int:course_id>/', views.course_detail, name='detail'),
    path('create/', views.course_create, name='create'),
    path('import/', views.course_import, name='import'),
    path('<int:course_id>/edit/', views.course_edit, name='edit'),
    path('<int:course_id>/delete/', views.course_delete, name='delete'),
    path('<int:course_id>/offerings/create/', views.offering_create, name='offering_create'),
    path('offerings/<int:offering_id>/edit/', views.offering_edit, name='offering_edit'),
    path('offerings/<int:offering_id>/delete/', views.offering_delete, name='offering_delete'),
    path('<int:course_id>/curriculum/', views.manage_curriculum, name='manage_curriculum'),
    path('<int:course_id>/curriculum/quick-add/', views.quick_add_to_program, name='quick_add_to_program'),
]
