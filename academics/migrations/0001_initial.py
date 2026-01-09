from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0003_add_default_semester'),
        ('students', '0004_alter_student_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('classification_scheme', models.CharField(choices=[('BSC', 'University (BSc) classification'), ('ND', 'Polytechnic (ND/HND) classification')], default='BSC', max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='CurriculumCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.CharField(choices=[('FIRST', 'First Semester'), ('SECOND', 'Second Semester'), ('SUMMER', 'Summer')], max_length=6)),
                ('is_compulsory', models.BooleanField(default=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.level')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='curriculum_courses', to='academics.program')),
            ],
            options={
                'unique_together': {('program', 'course', 'level', 'semester')},
            },
        ),
        migrations.CreateModel(
            name='Prerequisite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prereq_for', to='courses.course')),
                ('prerequisite_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='is_prereq_of', to='courses.course')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prerequisites', to='academics.program')),
            ],
            options={
                'unique_together': {('program', 'course', 'prerequisite_course')},
            },
        ),
    ]
