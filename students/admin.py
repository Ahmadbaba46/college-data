from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Level, Session, Student

# Register your models here.

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Session) 
class SessionAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'student_id', 'full_name', 'email', 'current_level', 
        'status', 'current_cgpa', 'academic_performance_indicator', 
        'risk_indicator'
    ]
    list_filter = [
        'status', 'current_level', 'entry_level', 'current_session',
        'gender', 'nationality', 'is_scholarship_recipient'
    ]
    search_fields = [
        'student_id', 'first_name', 'last_name', 'email', 
        'phone', 'emergency_contact'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'admission_date', 'current_cgpa',
        'total_units_attempted', 'total_units_passed', 'total_sessions_completed',
        'academic_performance_level', 'completion_rate', 'age_display',
        'years_enrolled_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'student_id', 'first_name', 'last_name', 'photo',
                'date_of_birth', 'gender', 'nationality', 'state_of_origin'
            )
        }),
        ('Contact Information', {
            'fields': (
                'email', 'phone', 'address', 'local_government'
            )
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact', 'emergency_contact_relationship',
                'emergency_phone', 'emergency_email'
            )
        }),
        ('Academic Information', {
            'fields': (
                'entry_level', 'current_level', 'current_session', 'entry_session',
                'status', 'admission_date', 'graduation_date'
            )
        }),
        ('Academic Performance (Read-only)', {
            'fields': (
                'current_cgpa', 'academic_performance_level',
                'total_units_attempted', 'total_units_passed',
                'total_sessions_completed', 'completion_rate'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': (
                'is_scholarship_recipient', 'special_needs', 'notes'
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': (
                'created_at', 'updated_at', 'age_display', 'years_enrolled_display'
            ),
            'classes': ('collapse',)
        })
    )
    
    list_editable = ['status']
    list_per_page = 25
    
    actions = [
        'update_academic_metrics', 'export_student_data', 'mark_as_graduated'
    ]
    
    def academic_performance_indicator(self, obj):
        """Visual indicator for academic performance"""
        if obj.current_cgpa >= 3.5:
            color = 'green'
            symbol = '🟢'
        elif obj.current_cgpa >= 3.0:
            color = 'blue'
            symbol = '🔵'
        elif obj.current_cgpa >= 2.5:
            color = 'orange'
            symbol = '🟡'
        elif obj.current_cgpa >= 2.0:
            color = 'red'
            symbol = '🔴'
        else:
            color = 'darkred'
            symbol = '🔴'
        
        return format_html(
            '<span style="color: {};">{} {:.2f}</span>',
            color, symbol, obj.current_cgpa
        )
    academic_performance_indicator.short_description = 'CGPA'
    academic_performance_indicator.admin_order_field = 'current_cgpa'
    
    def risk_indicator(self, obj):
        """Show if student is at academic risk"""
        if obj.is_at_risk:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ AT RISK</span>'
            )
        return format_html(
            '<span style="color: green;">✅ Good</span>'
        )
    risk_indicator.short_description = 'Risk Status'
    
    def age_display(self, obj):
        """Display calculated age"""
        age = obj.get_age()
        return f"{age} years" if age else "Not available"
    age_display.short_description = 'Age'
    
    def years_enrolled_display(self, obj):
        """Display years enrolled"""
        years = obj.years_enrolled()
        return f"{years} years" if years else "Not available"
    years_enrolled_display.short_description = 'Years Enrolled'
    
    def update_academic_metrics(self, request, queryset):
        """Update academic metrics for selected students"""
        updated = 0
        for student in queryset:
            student.update_academic_metrics()
            updated += 1
        
        self.message_user(
            request,
            f'Successfully updated academic metrics for {updated} students.'
        )
    update_academic_metrics.short_description = "Update academic metrics"
    
    def export_student_data(self, request, queryset):
        """Export selected student data"""
        self.message_user(
            request,
            f'Export functionality for {queryset.count()} students (implementation needed).'
        )
    export_student_data.short_description = "Export student data"
    
    def mark_as_graduated(self, request, queryset):
        """Mark selected students as graduated"""
        updated = 0
        for student in queryset.filter(status='active'):
            student.change_status('graduated', 'Bulk graduation', request.user)
            updated += 1
        
        self.message_user(
            request,
            f'Successfully marked {updated} students as graduated.'
        )
    mark_as_graduated.short_description = "Mark as graduated"
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related(
            'current_level', 'entry_level', 'current_session'
        )
