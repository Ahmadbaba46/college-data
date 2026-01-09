from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit_log', '0002_logentry_delete_log'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='action',
            field=models.CharField(
                choices=[
                    ('CREATE', 'Create'),
                    ('READ', 'Read'),
                    ('UPDATE', 'Update'),
                    ('DELETE', 'Delete'),
                    ('LOGIN', 'Login'),
                    ('LOGOUT', 'Logout'),
                    ('ASSIGN', 'Assign'),
                    ('ENROLL', 'Enroll'),
                    ('EXPORT', 'Export'),
                    ('IMPORT', 'Import'),
                    ('CALCULATE', 'Calculate'),
                    ('PROMOTE', 'Promote'),
                    ('STATUS_CHANGE', 'Status Change'),
                ],
                max_length=20,
            ),
        ),
    ]
