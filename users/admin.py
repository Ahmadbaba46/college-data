from django.contrib import admin

from users.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'teacher')
    search_fields = ('user__username', 'teacher__staff_id', 'teacher__first_name', 'teacher__last_name')
