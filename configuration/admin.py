from django.contrib import admin

from configuration.models import CollegeSettings


@admin.register(CollegeSettings)
class CollegeSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'college_name',
    )
    fields = (
        'college_name',
        'college_address',
        'college_logo',
        'principal_signature',
        'signature',
        'letterhead',
    )

