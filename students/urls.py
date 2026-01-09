from django.urls import path
from students import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('<int:student_id>/', views.student_detail, name='detail'),
    path('create/', views.student_create, name='create'),
    path('<int:student_id>/edit/', views.student_edit, name='edit'),
    path('<int:student_id>/delete/', views.student_delete, name='delete'),
    path('promote/', views.student_promote, name='promote'),
    path('import/', views.student_import, name='import'),
    path('bulk-assign-program/', views.bulk_assign_program, name='bulk_assign_program'),
    
    # HTMX partials
    path('partials/search/', views.student_search_partial, name='search_partial'),
    path('partials/promotion-preview/', views.promotion_preview_partial, name='promotion_preview_partial'),
]
