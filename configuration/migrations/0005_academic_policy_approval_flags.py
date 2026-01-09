from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0004_academic_policy_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicpolicysettings',
            name='require_approved_for_exports',
            field=models.BooleanField(default=False, help_text='If true, grade exports only include APPROVED grades.'),
        ),
        migrations.AddField(
            model_name='academicpolicysettings',
            name='require_approved_for_metrics',
            field=models.BooleanField(default=False, help_text='If true, CGPA/metrics computations only count APPROVED grades.'),
        ),
        migrations.AddField(
            model_name='academicpolicysettings',
            name='require_approved_for_transcripts',
            field=models.BooleanField(default=False, help_text='If true, transcripts only count APPROVED grades for GPA/CGPA (unapproved show as pending).'),
        ),
    ]
