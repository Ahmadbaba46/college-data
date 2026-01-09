from django.core.management.base import BaseCommand
from students.models import Student, Level
from django.db.models import Count

class Command(BaseCommand):
    help = 'Generate a report on the distribution of students per level'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Student Distribution by Level Report'))

        level_distribution = Student.objects.values('current_level__name').annotate(student_count=Count('id')).order_by('current_level__name')

        if level_distribution:
            for item in level_distribution:
                self.stdout.write(f'- Level: {item["current_level__name"]}, Students: {item["student_count"]}')
        else:
            self.stdout.write(self.style.WARNING('No students found.'))
