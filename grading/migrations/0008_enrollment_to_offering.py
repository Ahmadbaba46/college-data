from django.db import migrations, models
import django.db.models.deletion


def forwards_create_offerings_and_link(apps, schema_editor):
    Enrollment = apps.get_model('grading', 'Enrollment')
    CourseOffering = apps.get_model('courses', 'CourseOffering')

    # Create offerings from existing enrollments
    for e in Enrollment.objects.select_related('course', 'session').all():
        offering, _ = CourseOffering.objects.get_or_create(
            course_id=e.course_id,
            session_id=e.session_id,
            semester=e.semester,
            level_id=None,
            defaults={'is_active': True},
        )
        e.course_offering_id = offering.id
        e.save(update_fields=['course_offering'])


def backwards_unlink(apps, schema_editor):
    Enrollment = apps.get_model('grading', 'Enrollment')
    Enrollment.objects.update(course_offering=None)


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_courseoffering'),
        ('grading', '0007_add_summer_semester'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='course_offering',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='courses.courseoffering'),
        ),
        migrations.RunPython(forwards_create_offerings_and_link, backwards_unlink),
        migrations.AlterField(
            model_name='enrollment',
            name='course_offering',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.courseoffering'),
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('student', 'course_offering')},
        ),
        migrations.RemoveField(model_name='enrollment', name='course'),
        migrations.RemoveField(model_name='enrollment', name='session'),
        migrations.RemoveField(model_name='enrollment', name='semester'),
    ]
