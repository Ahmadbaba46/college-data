from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from users.models import Role


DEFAULT_ROLES = [
    ('Admin', 'Full system administrator with all permissions'),
    ('DataEntry', 'Data entry staff - can manage students, courses, and enrollments'),
    ('Teacher', 'Teacher - can view assigned courses and manage grades'),
]


class Command(BaseCommand):
    help = 'Create default RBAC roles in both Role model and Django Groups'

    def handle(self, *args, **options):
        role_created = 0
        group_created = 0
        
        for name, description in DEFAULT_ROLES:
            # Create Role model entry
            role, was_created = Role.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if was_created:
                role_created += 1
                self.stdout.write(f'  Created Role: {name}')
            
            # Also create Django Group for backward compatibility
            _g, was_created = Group.objects.get_or_create(name=name)
            if was_created:
                group_created += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Roles setup complete. New roles: {role_created}, New groups: {group_created}'
        ))
