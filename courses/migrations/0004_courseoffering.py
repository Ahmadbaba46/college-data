from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_add_default_semester'),
        ('students', '0004_alter_student_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseOffering',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.CharField(choices=[('FIRST', 'First Semester'), ('SECOND', 'Second Semester'), ('SUMMER', 'Summer')], default='FIRST', max_length=6)),
                ('capacity', models.PositiveIntegerField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offerings', to='courses.course')),
                ('level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.level')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.session')),
            ],
            options={
                'unique_together': {('course', 'session', 'semester', 'level')},
            },
        ),
    ]
