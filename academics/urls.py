from django.urls import path
from academics import views

app_name = 'academics'

urlpatterns = [
    path('programs/', views.program_list, name='program_list'),
    path('programs/<int:program_id>/', views.program_detail, name='program_detail'),
    path('programs/create/', views.program_create, name='program_create'),
    path('programs/<int:program_id>/edit/', views.program_edit, name='program_edit'),
    
    # Curriculum management
    path('programs/<int:program_id>/curriculum/add/', views.curriculum_add, name='curriculum_add'),
    path('programs/<int:program_id>/curriculum/<int:curriculum_id>/remove/', views.curriculum_remove, name='curriculum_remove'),
    path('programs/<int:program_id>/curriculum/copy/', views.copy_curriculum, name='copy_curriculum'),
    
    # Prerequisites management
    path('programs/<int:program_id>/prerequisites/', views.prerequisites_manage, name='prerequisites_manage'),
    path('programs/<int:program_id>/prerequisites/add/', views.prerequisite_add, name='prerequisite_add'),
    path('programs/<int:program_id>/prerequisites/<int:prereq_id>/remove/', views.prerequisite_remove, name='prerequisite_remove'),
    
    # Programs import
    path('programs/import/', views.program_import, name='program_import'),
]
